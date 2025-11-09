from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase
from models.schemas import ExpenseCreate
from decimal import Decimal

getcontext().prec = 28  # High precision for intermediate sums
CENTS = Decimal("0.01")

router = APIRouter()


def _q2(value: Decimal) -> Decimal:
    """Quantize to 2 decimals with bankers-safe rounding."""
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def _zeroish(value: Decimal) -> bool:
    """Treat tiny residuals as zero (e.g., 0.00…1 from division)."""
    return value.copy_abs() < Decimal("0.005")


def _compute_group_balances_decimal(group_id: str) -> Dict[str, Decimal]:
    """Return balances as Decimal: +owed / -owes, per user_id."""
    members = supabase.table("group_members").select("user_id").eq("group_id", group_id).execute().data
    user_ids = [member["user_id"] for member in members]
    balances: Dict[str, Decimal] = {user_id: Decimal("0") for user_id in user_ids}

    expenses = supabase.table("expenses").select("*").eq("group_id", group_id).execute().data
    if not expenses:
        return {user_id: _q2(balance) for user_id, balance in balances.items()}

    expense_ids = []
    for expense in expenses:
        expense_ids.append(expense["id"])
        payer = expense["payer_id"]
        amount = Decimal(str(expense["amount"]))
        if payer in balances:
            balances[payer] += amount

    splits = supabase.table("expense_splits").select("*").in_("expense_id", expense_ids).execute().data
    for split in splits:
        user_id = split["user_id"]
        share = Decimal(str(split["share"]))
        if user_id in balances:
            balances[user_id] -= share

    output: Dict[str, Decimal] = {}
    for user_id, balance in balances.items():
        quantized = _q2(balance)
        output[user_id] = Decimal("0.00") if _zeroish(quantized) else quantized
    return output


def _settle_min_transactions(balances: Dict[str, Decimal]) -> List[dict]:
    """
    Greedy settle: match largest creditor with largest debtor.
    Returns list of {from, to, amount} with amount as string (2 decimals).
    """
    creditors = []  # (user_id, +amount)
    debtors = []    # (user_id, -amount)

    for user_id, balance in balances.items():
        if balance > 0:
            creditors.append([user_id, balance])
        elif balance < 0:
            debtors.append([user_id, -balance])

    creditors.sort(key=lambda item: item[1], reverse=True)
    debtors.sort(key=lambda item: item[1], reverse=True)

    settlements: List[dict] = []
    ci = 0
    di = 0
    while ci < len(creditors) and di < len(debtors):
        creditor_user, creditor_amount = creditors[ci]
        debtor_user, debtor_amount = debtors[di]

        pay = _q2(creditor_amount if creditor_amount <= debtor_amount else debtor_amount)
        if pay > 0:
            settlements.append({
                "from": debtor_user,
                "to": creditor_user,
                "amount": f"{pay:.2f}",
            })

        creditor_amount = _q2(creditor_amount - pay)
        debtor_amount = _q2(debtor_amount - pay)

        if _zeroish(creditor_amount) or creditor_amount == 0:
            ci += 1
        else:
            creditors[ci][1] = creditor_amount

        if _zeroish(debtor_amount) or debtor_amount == 0:
            di += 1
        else:
            debtors[di][1] = debtor_amount

    return settlements

@router.post("/")
def add_expense(payload: ExpenseCreate):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add expense: {str(e)}")


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
    balances = _compute_group_balances_decimal(group_id)
    settlements = _settle_min_transactions(balances)
    return {
        "group_id": group_id,
        "balances": {user_id: float(amount) for user_id, amount in balances.items()},
        "settlements": settlements,
    }


@router.get("/group/{group_id}/settle-up")
def settle_up(group_id: str):
    """
    Returns a minimal set of transactions (from -> to -> amount)
    that settles all balances for the group.
    """

    # Step 1: recompute fresh balances (always authoritative)
    balances = _compute_group_balances_decimal(group_id)

    # Step 2: ensure total = 0.00 (no money lost)
    total = sum(balances.values(), Decimal("0"))
    if not _zeroish(_q2(total)):
        raise HTTPException(
            status_code=500,
            detail=f"Inconsistent balances (sum={_q2(total)})"
        )

    # Step 3: generate minimal transaction plan
    plan = _settle_min_transactions(balances)

    # Step 4: return structured response
    return {
        "group_id": group_id,
        "balances": {u: f"{_q2(v):.2f}" for u, v in balances.items()},
        "transactions": plan
    }
