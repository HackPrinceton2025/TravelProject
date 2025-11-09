from fastapi import APIRouter, HTTPException
from utils.supabase_client import supabase

router = APIRouter()

@router.post("/join")
def join_group(invite_code: str, user_id: str):
    group = supabase.table("groups").select("id").eq("invite_code", invite_code).execute()
    if not group.data:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    group_id = group.data[0]["id"]
    supabase.table("group_members").insert({"group_id": group_id, "user_id": user_id}).execute()
    return {"message": "Joined group successfully", "group_id": group_id}


@router.get("/{group_id}")
def list_members(group_id: str):
    try:
        # Join with users table to get user names
        res = supabase.table("group_members") \
            .select("*, users(id, name, email)") \
            .eq("group_id", group_id) \
            .execute()
        
        # Flatten the nested users object into user_name and user_email fields
        data = res.data or []
        for member in data:
            users_data = member.get("users")
            if users_data and isinstance(users_data, dict):
                # User exists in users table
                member["user_name"] = users_data.get("name") or users_data.get("email") or "Unknown"
                member["user_email"] = users_data.get("email")
            else:
                # Fallback if user not found in users table
                member["user_name"] = "Unknown User"
                member["user_email"] = None
            # Remove nested users object to avoid confusion
            if "users" in member:
                del member["users"]
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch group members: {str(e)}")
