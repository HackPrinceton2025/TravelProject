from typing import Dict, List
from fastapi import APIRouter
from models.schemas import Poll, PollCreate

router = APIRouter(tags=["polls"])


@router.get("/{group_id}", response_model=List[Poll])
def list_polls(group_id: str) -> List[Poll]:
    return []


@router.post("/", response_model=Poll)
def create_poll(payload: PollCreate) -> Poll:
    return Poll(
        id="poll_1",
        group_id=payload.group_id,
        question=payload.question,
        options=payload.options,
        votes={},
    )


@router.post("/{poll_id}/vote", response_model=Poll)
def vote_poll(poll_id: str, vote: Dict[str, str]) -> Poll:
    # Placeholder vote structure: {"option": "Option A"}
    option = vote.get("option", "")
    return Poll(
        id=poll_id,
        group_id="grp_1",
        question="Placeholder question",
        options=["Option A", "Option B"],
        votes={option: 1} if option else {},
    )


