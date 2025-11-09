from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.tools.preferences import update_user_preferences
from utils.supabase_client import supabase

router = APIRouter(prefix="/preferences", tags=["preferences"])


class PreferenceUpdateRequest(BaseModel):
    group_id: str
    user_id: str
    interests: Optional[List[str]] = None
    budget_max: Optional[int] = None
    departure_city: Optional[str] = None


@router.get("/status")
def get_preference_status(group_id: str, user_id: str):
    """
    Return whether the user already set key preference fields for this group.
    Used to decide if the onboarding prompt should be shown.
    """
    response = (
        supabase.table("user_preferences")
        .select("interests, budget_max, departure_city")
        .eq("group_id", group_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    pref = response.data[0] if response.data else None

    interests = pref.get("interests") if pref else []
    budget_max = pref.get("budget_max") if pref else None
    departure_city = pref.get("departure_city") if pref else None

    return {
        "has_interests": bool(interests),
        "has_budget": budget_max is not None,
        "has_departure_city": bool(departure_city),
        "interests": interests or [],
        "budget_max": budget_max,
        "departure_city": departure_city,
    }


@router.post("/update")
def update_preferences(payload: PreferenceUpdateRequest):
    """
    Proxy to the agent preference tool so the frontend can set specific fields.
    Only updates the fields included in the payload.
    """
    if (
        payload.interests is None
        and payload.budget_max is None
        and payload.departure_city is None
    ):
        raise HTTPException(
            status_code=400, detail="Provide at least one preference field to update"
        )

    try:
        result = update_user_preferences(
            user_id=payload.user_id,
            group_id=payload.group_id,
            interests=payload.interests,
            budget_max=payload.budget_max,
            departure_city=payload.departure_city,
        )
        updated = result.get("metadata", {}).get("updated_preferences", {})
        return {
            "success": True,
            "updated_preferences": updated,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to update preferences: {str(exc)}"
        )
