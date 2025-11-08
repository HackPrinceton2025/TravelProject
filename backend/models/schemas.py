from pydantic import BaseModel
from typing import Any, Optional

# Schema for creating a new group
class GroupCreate(BaseModel):
    name: str
    created_by: Optional[str] = None  # later we’ll connect to users

# Schema for sending a message
class MessageCreate(BaseModel):
    group_id: str
    sender_id: str
    kind: Optional[str] = "text"
    body: Any  # can hold {"text": "hello"} or more complex AI content
