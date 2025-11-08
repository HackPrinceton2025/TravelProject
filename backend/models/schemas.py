from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Group(BaseModel):
    id: str
    name: str


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1)


class Message(BaseModel):
    id: str
    group_id: str
    sender: str
    content: str
    created_at: Optional[datetime] = None


class MessageCreate(BaseModel):
    group_id: str
    sender: str
    content: str


class Poll(BaseModel):
    id: str
    group_id: str
    question: str
    options: List[str]
    votes: Dict[str, int] = {}


class PollCreate(BaseModel):
    group_id: str
    question: str
    options: List[str]


