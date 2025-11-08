from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase

router = APIRouter()

@router.post("/join")
def join_group(invite_code: str, user_id: str):
    # find the group by invite code
    group = supabase.table("groups").select("id").eq("invite_code", invite_code).execute()
    if not group.data:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    group_id = group.data[0]["id"]
    supabase.table("group_members").insert({"group_id": group_id, "user_id": user_id}).execute()
    return {"message": "Joined group successfully", "group_id": group_id}

@router.get("/{group_id}")
def list_members(group_id: str):
    res = supabase.table("group_members").select("*").eq("group_id", group_id).execute()
    return res.data
