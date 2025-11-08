"""
New Poll System API (v2)
User-facing endpoints for voting in chat UI
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.supabase_client import supabase
from datetime import datetime

router = APIRouter(prefix="/polls/v2", tags=["polls-v2"])


class VoteRequest(BaseModel):
    """User votes on a poll option"""
    poll_id: str
    user_id: str
    option_ids: List[str]  # List of selected option IDs


@router.post("/vote")
async def cast_vote(payload: VoteRequest):
    """
    Cast a vote on a poll.
    Called by frontend when user clicks a poll option in chat UI.
    
    Flow:
    1. User clicks option in poll UI
    2. Frontend calls this endpoint
    3. Vote is recorded in DB
    4. Check if majority reached
    5. If yes, trigger AI notification
    """
    try:
        poll_id = payload.poll_id
        user_id = payload.user_id
        option_ids = payload.option_ids
        
        # Get poll
        poll = supabase.table("polls")\
            .select("*")\
            .eq("id", poll_id)\
            .single()\
            .execute().data
        
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        if poll["status"] != "active":
            raise HTTPException(status_code=400, detail="Poll is not active")
        
        # Check voting type
        if poll["voting_type"] == "single_choice" and len(option_ids) > 1:
            raise HTTPException(status_code=400, detail="Only one option allowed for single choice")
        
        # Delete previous votes by this user (allow vote change)
        supabase.table("poll_votes")\
            .delete()\
            .eq("poll_id", poll_id)\
            .eq("user_id", user_id)\
            .execute()
        
        # Insert new votes
        vote_rows = [
            {
                "poll_id": poll_id,
                "user_id": user_id,
                "option_id": option_id,
                "voted_at": datetime.now().isoformat()
            }
            for option_id in option_ids
        ]
        
        supabase.table("poll_votes").insert(vote_rows).execute()
        
        # Update vote counts on options
        for option_id in option_ids:
            # Count votes for this option
            vote_count = len(supabase.table("poll_votes")\
                .select("id")\
                .eq("option_id", option_id)\
                .execute().data)
            
            supabase.table("poll_options")\
                .update({"vote_count": vote_count})\
                .eq("id", option_id)\
                .execute()
        
        # Get updated poll status
        from agent.tools.polls import get_poll_status
        status_result = get_poll_status(poll_id, poll["group_id"])
        
        poll_data = status_result["cards"][0]["data"]
        
        return {
            "success": True,
            "message": "Vote recorded",
            "poll_id": poll_id,
            "has_majority": poll_data["has_majority"],
            "leader": poll_data["leader"],
            "total_votes": poll_data["total_votes"],
            "participation_rate": poll_data["participation_rate"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record vote: {str(e)}")


@router.get("/{poll_id}")
async def get_poll(poll_id: str):
    """Get current poll data with vote counts"""
    try:
        poll = supabase.table("polls")\
            .select("*")\
            .eq("id", poll_id)\
            .single()\
            .execute().data
        
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        # Get options with votes
        options = supabase.table("poll_options")\
            .select("*")\
            .eq("poll_id", poll_id)\
            .order("order_index")\
            .execute().data
        
        # Get votes
        votes = supabase.table("poll_votes")\
            .select("user_id, option_id")\
            .eq("poll_id", poll_id)\
            .execute().data
        
        voted_users = list(set(v["user_id"] for v in votes))
        
        # Calculate percentages
        total_votes = len(voted_users)
        for opt in options:
            opt_votes = len([v for v in votes if v["option_id"] == opt["id"]])
            opt["votes"] = opt_votes
            opt["percentage"] = (opt_votes / total_votes * 100) if total_votes > 0 else 0
        
        return {
            "poll_id": poll["id"],
            "group_id": poll["group_id"],
            "question": poll["question"],
            "poll_type": poll["poll_type"],
            "voting_type": poll["voting_type"],
            "status": poll["status"],
            "options": options,
            "total_votes": total_votes,
            "voted_users": voted_users,
            "created_at": poll["created_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get poll: {str(e)}")


@router.get("/group/{group_id}/active")
async def get_active_polls(group_id: str):
    """Get all active polls for a group"""
    try:
        polls = supabase.table("polls")\
            .select("*")\
            .eq("group_id", group_id)\
            .eq("status", "active")\
            .order("created_at", desc=True)\
            .execute().data
        
        return {
            "group_id": group_id,
            "polls": polls,
            "total": len(polls)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get polls: {str(e)}")
