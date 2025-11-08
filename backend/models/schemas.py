from pydantic import BaseModel, condecimal
from typing import List, Optional

class ExpenseParticipant(BaseModel):
    user_id: str
    share: Optional[condecimal(ge=0)] = None  # optional for equal split

class ExpenseCreate(BaseModel):
    group_id: str
    payer_id: str          # default = current user later (auth); for now pass UUID
    description: Optional[str] = None
    amount: condecimal(ge=0)
    split_between: List[ExpenseParticipant]  # participants (including payer or not, your choice)
