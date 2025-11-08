from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase

router = APIRouter()

@router.get("/")
def get_messages(group_id: str):
    response = supabase.table("messages").select("*").eq("group_id", group_id).execute()
    return response.data

@router.post("/")
def send_message(payload: dict):
    data = {
        "group_id": payload["group_id"],
        "sender_id": payload["sender_id"],
        "kind": payload.get("kind", "text"),
        "body": payload.get("body", {}),
    }
    res = supabase.table("messages").insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed")
    return res.data[0]
