from typing import List
from fastapi import APIRouter
from models.schemas import Group, GroupCreate

router = APIRouter(tags=["groups"])


@router.get("/", response_model=List[Group])
def list_groups() -> List[Group]:
    # Placeholder in-memory list
    return []


@router.post("/", response_model=Group)
def create_group(payload: GroupCreate) -> Group:
    # Placeholder creation
    return Group(id="grp_1", name=payload.name)


@router.get("/{group_id}", response_model=Group)
def get_group(group_id: str) -> Group:
    # Placeholder retrieval
    return Group(id=group_id, name=f"Group {group_id}")


