from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List, Optional
from statistics import median
from utils.supabase_client import supabase
from models.schemas import (
    PollStart, PreferenceCreate, PollSuggest, VoteCreate, ConfirmChoice
)

router = APIRouter()

# ---------- helpers ----------
def _get_group_member_count(group_id: str) -> int:
    res = supabase.table("group_members").select("id", count="exact").eq("group_id", group_id).execute()
    return res.count or 0

def _get_distinct_pref_count(poll_id: str) -> int:
    # distinct user_id count
    res = supabase.rpc("exec_sql", {
        "sql": f"select count(distinct user_id) as c from poll_preferences where poll_id = '{poll_id}'"
    }).execute() if False else None  # no RPC installed; fallback below

    # fallback: fetch and count in app
    rows = supabase.table("poll_preferences").select("user_id").eq("poll_id", poll_id).execute().data
    return len(set(row["user_id"] for row in rows))

def _get_poll(poll_id: str) -> Dict[str, Any]:
    res = supabase.table("polls").select("*").eq("id", poll_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Poll not found")
    return res.data

def _require_creator(poll: Dict[str, Any], user_id: str):
    if poll["created_by"] != user_id:
        raise HTTPException(status_code=403, detail="Only poll creator can perform this action")

def _compute_vote_ratio(suggestion_id: str) -> Dict[str, float]:
    rows = supabase.table("poll_votes").select("vote").eq("suggestion_id", suggestion_id).execute().data
    if not rows:
        return {"yes": 0.0, "total": 0.0, "ratio": 0.0}
    yes = sum(1 for r in rows if r["vote"])
    total = len(rows)
    return {"yes": float(yes), "total": float(total), "ratio": (yes / total) if total else 0.0}

def _poll_summary(poll_id: str) -> Dict[str, Any]:
    poll = _get_poll(poll_id)
    prefs = supabase.table("poll_preferences").select("*").eq("poll_id", poll_id).execute().data
    # aggregate place_type counts
    type_counts: Dict[str, int] = {}
    budgets: List[int] = []
    interests_counts: Dict[str, int] = {}

    for p in prefs:
        pt = p.get("place_type")
        if pt:
            type_counts[pt] = type_counts.get(pt, 0) + 1
        b = p.get("budget")
        if isinstance(b, int):
            budgets.append(b)
        ints = p.get("interests") or []
        if isinstance(ints, list):
            for tag in ints:
                interests_counts[tag] = interests_counts.get(tag, 0) + 1

    med_budget: Optional[float] = float(median(budgets)) if budgets else None

    # suggestions + vote tallies
    suggs = supabase.table("poll_suggestions").select("*").eq("poll_id", poll_id).execute().data
    out_suggs: List[Dict[str, Any]] = []
    for s in suggs:
        r = _compute_vote_ratio(s["id"])
        out_suggs.append({
            **s,
            "votes": {"yes": r["yes"], "total": r["total"], "ratio": round(r["ratio"], 2)}
        })

    return {
        "poll": poll,
        "aggregates": {
            "place_type_counts": type_counts,
            "median_budget": med_budget,
            "interests_counts": interests_counts
        },
        "suggestions": out_suggs
    }

# ---------- endpoints ----------

@router.post("/start")
def start_poll(payload: PollStart):
    # mode & required fields
    if payload.mode == "discover":
        if payload.days is None:
            raise HTTPException(status_code=400, detail="days is required for discover mode")
        status = "collecting"
        final_destination = None
    elif payload.mode == "fixed":
        if not payload.final_destination or payload.days is None:
            raise HTTPException(status_code=400, detail="final_destination and days are required for fixed mode")
        status = "locked"  # fixed destination locks immediately
        final_destination = payload.final_destination
    else:
        raise HTTPException(status_code=400, detail="invalid mode")

    res = supabase.table("polls").insert({
        "group_id": payload.group_id,
        "created_by": payload.created_by,
        "mode": payload.mode,
        "status": status,
        "final_destination": final_destination,
        "days": payload.days
    }).execute()
    poll = res.data[0]

    # For discover: notify chat (optional); For fixed: trigger itinerary-needed (out of scope)
    return poll


@router.post("/preferences")
def submit_preferences(payload: PreferenceCreate):
    # upsert preference per (poll_id, user_id) by app logic: delete old + insert new
    # simplest: insert new row (duplicates fine in hackathon) OR emulate upsert by delete-then-insert:
    supabase.table("poll_preferences").delete().eq("poll_id", payload.poll_id).eq("user_id", payload.user_id).execute()
    supabase.table("poll_preferences").insert({
        "poll_id": payload.poll_id,
        "user_id": payload.user_id,
        "place_type": payload.place_type,
        "budget": payload.budget,
        "interests": payload.interests
    }).execute()

    # state transition: if >=50% of group members submitted -> ready_for_ai
    poll = _get_poll(payload.poll_id)
    members = _get_group_member_count(poll["group_id"])
    have = _get_distinct_pref_count(payload.poll_id)
    if members > 0 and have / members >= 0.5 and poll["status"] in ("planning", "collecting"):
        supabase.table("polls").update({"status": "ready_for_ai"}).eq("id", payload.poll_id).execute()

    return {"message": "preferences saved", "submitted": have, "members": members}


@router.post("/suggest")
def accept_suggestions(payload: PollSuggest):
    # Called by AI service (Aaron) or manually while testing
    poll = _get_poll(payload.poll_id)
    if poll["status"] not in ("ready_for_ai", "voting", "collecting"):
        # allow re-suggesting if in voting (to add more options)
        pass

    rows = []
    for s in payload.suggestions:
        rows.append({
            "poll_id": payload.poll_id,
            "place_name": s.place_name,
            "reason": s.reason,
            "est_budget": s.est_budget,
            "activities": s.activities,
            "fun_fact": s.fun_fact,
            "status": "open"
        })
    if rows:
        supabase.table("poll_suggestions").insert(rows).execute()

    # move to voting
    supabase.table("polls").update({"status": "voting"}).eq("id", payload.poll_id).execute()
    return {"message": "suggestions recorded", "count": len(rows)}


@router.post("/vote")
def vote_suggestion(payload: VoteCreate):
    # upsert vote per (suggestion_id, user_id)
    supabase.table("poll_votes").delete().eq("suggestion_id", payload.suggestion_id).eq("user_id", payload.user_id).execute()
    supabase.table("poll_votes").insert({
        "suggestion_id": payload.suggestion_id,
        "user_id": payload.user_id,
        "vote": payload.vote
    }).execute()

    # compute ratio and possibly approve
    r = _compute_vote_ratio(payload.suggestion_id)
    # 0.70 threshold; tune as needed
    if r["total"] >= 2 and r["ratio"] >= 0.70:
        supabase.table("poll_suggestions").update({"status": "approved"}).eq("id", payload.suggestion_id).execute()

    return {"message": "vote recorded", "yes": r["yes"], "total": r["total"], "ratio": round(r["ratio"], 2)}


@router.post("/confirm")
def confirm_choice(payload: ConfirmChoice):
    poll = _get_poll(payload.poll_id)
    _require_creator(poll, payload.confirmed_by)

    # validate suggestion matches poll
    sugg = supabase.table("poll_suggestions").select("*").eq("id", payload.suggestion_id).single().execute().data
    if not sugg or sugg["poll_id"] != payload.poll_id:
        raise HTTPException(status_code=400, detail="Suggestion does not belong to this poll")

    # lock poll + suggestion
    supabase.table("poll_suggestions").update({"status": "locked"}).eq("id", payload.suggestion_id).execute()
    supabase.table("polls").update({
        "status": "locked",
        "final_destination": sugg["place_name"]
    }).eq("id", payload.poll_id).execute()

    # (Optional) trigger itinerary-needed for AI here

    return {"message": "destination locked", "final_destination": sugg["place_name"]}


@router.get("/{poll_id}/summary")
def poll_summary(poll_id: str):
    return _poll_summary(poll_id)
