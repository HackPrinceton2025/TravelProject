from typing import List
from fastapi import APIRouter
from models.schemas import Message, MessageCreate

router = APIRouter(tags=["messages"])


@router.get("/{group_id}", response_model=List[Message])
def list_messages(group_id: str) -> List[Message]:
    # Placeholder: no persistence
    return []


@router.post("/", response_model=Message)
def create_message(payload: MessageCreate) -> Message:
    # Placeholder creation
    return Message(
        id="msg_1",
        group_id=payload.group_id,
        sender=payload.sender,
        content=payload.content,
    )


