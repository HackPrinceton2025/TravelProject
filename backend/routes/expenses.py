from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase
from models.schemas import ExpenseCreate

router = APIRouter()

@router.post("/")
def add_expense(payload: ExpenseCreate):
    data = payload.dict()
    group_id = data["group_id"]
    payer_id = data["payer_id"]
    amount   = float(data["amount"])
    parts    = data["split_between"]

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")
    if not parts:
        raise HTTPException(status_code=400, detail="Provide at least one participant")

    # If no custom shares provided, split equally among listed participants
    custom = any(p.get("share") is not None for p in parts)
    if not custom:
        equal = round(amount / len(parts), 2)
        for p in parts:
            p["share"] = equal
        # Adjust rounding remainder on the last participant
        remainder = round(amount - sum(float(p["share"]) for p in parts), 2)
        parts[-1]["share"] = round(float(parts[-1]["share"]) + remainder, 2)

    # Validate totals (allow tiny rounding error)
    total_shares = round(sum(float(p["share"]) for p in parts), 2)
    if abs(total_shares - amount) > 0.01:
        raise HTTPException(status_code=400, detail=f"Shares ({total_shares}) must sum to amount ({amount})")

    # Insert expense
    exp_res = supabase.table("expenses").insert({
        "group_id": group_id,
        "payer_id": payer_id,
        "description": data.get("description"),
        "amount": amount
    }).execute()
    if not exp_res.data:
        raise HTTPException(status_code=500, detail="Failed to create expense")
    expense = exp_res.data[0]

    # Insert splits (each participant owes their share)
    for p in parts:
        supabase.table("expense_splits").insert({
            "expense_id": expense["id"],
            "user_id": p["user_id"],
            "share": float(p["share"])
        }).execute()

    return {"message": "Expense added", "expense_id": expense["id"]}


@router.get("/group/{group_id}")
def list_group_expenses(group_id: str):
    # Get expenses with nested splits
    res = supabase.table("expenses") \
        .select("*, expense_splits(*)") \
        .eq("group_id", group_id) \
        .order("created_at") \
        .execute()
    return res.data


@router.get("/group/{group_id}/balances")
def compute_balances(group_id: str):
    """
    Net balance per user in the group:
      positive => others owe this user
      negative => this user owes others
    """
    # 1) Who are the members?
    members = supabase.table("group_members").select("user_id").eq("group_id", group_id).execute().data
    user_ids = [m["user_id"] for m in members]

    # Initialize balances
    balances = {u: 0.0 for u in user_ids}

    # 2) Sum paid per user
    expenses = supabase.table("expenses").select("*").eq("group_id", group_id).execute().data
    for e in expenses:
        payer = e["payer_id"]
        amt   = float(e["amount"])
        if payer in balances:
            balances[payer] += amt

    # 3) Sum owed per user (their splits)
    if expenses:
        exp_ids = [e["id"] for e in expenses]
        # Fetch all splits belonging to this group's expenses
        splits = supabase.table("expense_splits").select("*").in_("expense_id", exp_ids).execute().data
        for s in splits:
            u = s["user_id"]
            if u in balances:
                balances[u] -= float(s["share"])

    # Optional: round to 2 decimals
    for u in balances:
        balances[u] = round(balances[u], 2)

    return {"group_id": group_id, "balances": balances}
