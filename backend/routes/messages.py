from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase
from models.schemas import MessageCreate

router = APIRouter()

@router.get("/")
def get_messages(group_id: str):
    response = supabase.table("messages") \
        .select("*") \
        .eq("group_id", group_id) \
        .order("created_at") \
        .execute()
    return response.data

@router.post("/")
def send_message(payload: MessageCreate):
    data = payload.dict()

    # Optional hackathon guard: ensure sender is in the group
    members = supabase.table("group_members") \
        .select("user_id") \
        .eq("group_id", data["group_id"]) \
        .execute().data
    if data["sender_id"] not in [m["user_id"] for m in members]:
        raise HTTPException(status_code=403, detail="User not in group")

    res = supabase.table("messages").insert({
        "group_id": data["group_id"],
        "sender_id": data["sender_id"],
        "kind": data.get("kind", "text"),
        "body": data["body"]
    }).execute()

    if not res.data:
        raise HTTPException(status_code=500, detail="Message not inserted")
    return res.data[0]
