from fastapi import APIRouter
from utils.supabase_client import supabase

router = APIRouter()

@router.post("/")
def create_user(name: str, email: str = None):
    data = {"name": name, "email": email}
    res = supabase.table("users").insert(data).execute()
    return res.data[0]
