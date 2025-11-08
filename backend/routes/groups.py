import secrets
from fastapi import APIRouter
from utils.supabase_client import supabase
from models.schemas import GroupCreate

router = APIRouter()

@router.post("/")
def create_group(payload: GroupCreate):
    data = payload.dict()
    data["invite_code"] = secrets.token_hex(4)
    res = supabase.table("groups").insert(data).execute()
    return res.data[0]

@router.get("/")
def list_groups():
    res = supabase.table("groups").select("*").order("created_at").execute()
    return res.data
