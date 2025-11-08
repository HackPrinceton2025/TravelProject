from pydantic import BaseModel, condecimal
from typing import Any, Optional, List

# --- Groups & Messages ---

class GroupCreate(BaseModel):
    name: str
    created_by: Optional[str] = None  # later connected to users table

class MessageCreate(BaseModel):
    group_id: str
    sender_id: str
    kind: Optional[str] = "text"
    body: Any  # can hold {"text": "hello"} or more complex AI content

# --- Expense Splitting ---

class ExpenseParticipant(BaseModel):
    user_id: str
    share: Optional[condecimal(ge=0)] = None  # optional for equal split

class ExpenseCreate(BaseModel):
    group_id: str
    payer_id: str          # current user later (auth)
    description: Optional[str] = None
    amount: condecimal(ge=0)
    split_between: List[ExpenseParticipant]
