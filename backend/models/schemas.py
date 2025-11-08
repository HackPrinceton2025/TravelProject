from pydantic import BaseModel, condecimal, conint
from typing import Any, Optional, List, Literal, Dict

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

# --- Polls ---

class PollStart(BaseModel):
    group_id: str
    created_by: str
    mode: Literal['discover', 'fixed']
    days: Optional[conint(ge=1, le=30)] = None
    final_destination: Optional[str] = None  # required if mode='fixed'

class PreferenceCreate(BaseModel):
    poll_id: str
    user_id: str
    place_type: Optional[str] = None        # 'beach'|'mountain'|'city'|...
    budget: Optional[conint(ge=0)] = None   # per-person USD
    interests: Optional[List[str]] = None   # tags

class SuggestionItem(BaseModel):
    place_name: str
    reason: Optional[str] = None
    est_budget: Optional[int] = None
    activities: Optional[List[str]] = None
    fun_fact: Optional[str] = None

class PollSuggest(BaseModel):
    poll_id: str
    suggestions: List[SuggestionItem]

class VoteCreate(BaseModel):
    suggestion_id: str
    user_id: str
    vote: bool  # True=yes, False=no

class ConfirmChoice(BaseModel):
    poll_id: str
    suggestion_id: str
    confirmed_by: str
