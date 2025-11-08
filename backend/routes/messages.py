from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase
from models.schemas import MessageCreate

router = APIRouter()

@router.get("/")
def get_messages(group_id: str):
    response = supabase.table("messages").select("*").eq("group_id", group_id).execute()
    return response.data

@router.post("/")
def send_message(payload: MessageCreate):
    data = payload.dict()
    res = supabase.table("messages").insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed")
    return res.data[0]

