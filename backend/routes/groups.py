from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase

router = APIRouter()

@router.post("/")
def create_group(payload: dict):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Group name is required")

    res = supabase.table("groups").insert({"name": name}).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Group creation failed")
    return res.data[0]

@router.get("/")
def list_groups():
    res = supabase.table("groups").select("*").order("created_at").execute()
    return res.data
