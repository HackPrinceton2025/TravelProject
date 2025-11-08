"""
Poll Tools for Group Decision Making (AI-driven)
Allows AI agent to create polls during conversation and track voting progress.
"""
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from utils.supabase_client import supabase


def create_poll(
    group_id: str,
    question: str,
    options: List[Dict[str, Any]],
    created_by: str,
    poll_type: str = "custom",
    voting_type: str = "single_choice"
) -> Dict[str, Any]:
    """
    Create a voting poll that will be displayed in the chat UI.
    AI calls this when users want to vote on something.
    
    **Usage examples:**
    - User: "Let's vote on which hotel to book"
      → AI: create_poll(question="Which hotel?", options=[...hotel cards...])
    
    Args:
        group_id: ID of the travel group
        question: Question to ask (e.g., "Which hotel should we book?")
        options: List of options with {text, metadata} (e.g., [{"text": "Hotel A", "metadata": {"price": 120}}])
        created_by: User ID who initiated the poll (from context)
        poll_type: Type - 'destination', 'hotel', 'flight', 'restaurant', 'activity', 'date', 'time', 'custom'
        voting_type: 'single_choice' or 'multiple_choice'
        
    Returns:
        Poll card that frontend will render as voting UI
    """
    try:
        poll_id = f"poll_{uuid.uuid4().hex[:12]}"
        
        # Create poll in database
        poll_data = {
            "id": poll_id,
            "group_id": group_id,
            "created_by": created_by,
            "question": question,
            "poll_type": poll_type,
            "voting_type": voting_type,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("polls").insert(poll_data).execute()
        
        # Create options
        option_rows = []
        for i, opt in enumerate(options):
            option_id = f"opt_{poll_id}_{i}"
            option_rows.append({
                "id": option_id,
                "poll_id": poll_id,
                "text": opt.get("text", f"Option {i+1}"),
                "metadata": opt.get("metadata"),
                "vote_count": 0,
                "order_index": i
            })
        
        if option_rows:
            supabase.table("poll_options").insert(option_rows).execute()
        
        # Return poll card for frontend
        return {
            "type": "poll_created",
            "cards": [
                {
                    "type": "poll",
                    "id": poll_id,
                    "data": {
                        "poll_id": poll_id,
                        "question": question,
                        "poll_type": poll_type,
                        "voting_type": voting_type,
                        "status": "active",
                        "options": [
                            {
                                "option_id": row["id"],
                                "text": row["text"],
                                "metadata": row["metadata"],
                                "votes": 0,
                                "percentage": 0
                            }
                            for row in option_rows
                        ],
                        "total_votes": 0,
                        "created_at": poll_data["created_at"]
                    }
                }
            ],
            "metadata": {
                "poll_id": poll_id,
                "group_id": group_id,
                "action": "display_poll_ui"  # Signal to frontend
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to create poll: {str(e)}",
                    "error_type": "database_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def get_group_polls(
    group_id: str,
    status: Optional[str] = None,
    poll_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all polls for a group, with optional filtering.
    Returns basic poll information without detailed vote analysis.
    
    **When to use:**
    - User asks: "Show me all polls"
    - User asks: "What polls are active?"
    - User asks: "Show me hotel polls"
    
    **Usage examples:**
    - "Show all polls" → get_group_polls(group_id=GROUP_ID)
    - "Show active polls" → get_group_polls(group_id=GROUP_ID, status="active")
    - "Show hotel polls" → get_group_polls(group_id=GROUP_ID, poll_type="hotel")
    
    Args:
        group_id: ID of the travel group
        status: Optional filter - 'active', 'confirmed', or 'cancelled'
        poll_type: Optional filter - 'hotel', 'restaurant', 'destination', 'activity', 'custom', etc.
        
    Returns:
        List of poll cards with basic information (question, options, vote counts)
    """
    try:
        # Build query
        query = supabase.table("polls")\
            .select("*")\
            .eq("group_id", group_id)\
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        if poll_type:
            query = query.eq("poll_type", poll_type)
        
        polls_result = query.execute()
        
        if not polls_result.data:
            return {
                "type": "polls_list",
                "cards": [],
                "metadata": {
                    "group_id": group_id,
                    "total_polls": 0,
                    "message": "No polls found"
                }
            }
        
        # For each poll, get options with vote counts
        poll_cards = []
        for poll in polls_result.data:
            poll_id = poll["id"]
            
            # Get options
            options = supabase.table("poll_options")\
                .select("*")\
                .eq("poll_id", poll_id)\
                .order("order_index")\
                .execute().data
            
            # Get total votes (count distinct users)
            votes = supabase.table("poll_votes")\
                .select("user_id")\
                .eq("poll_id", poll_id)\
                .execute().data
            
            voted_users = list(set(v["user_id"] for v in votes))
            total_votes = len(voted_users)
            
            # Calculate percentages for each option
            for opt in options:
                opt_votes = len([v for v in votes if v.get("option_id") == opt["id"]])
                opt["votes"] = opt_votes
                opt["percentage"] = (opt_votes / total_votes * 100) if total_votes > 0 else 0
            
            poll_cards.append({
                "type": "poll",
                "id": poll_id,
                "data": {
                    "poll_id": poll_id,
                    "question": poll["question"],
                    "poll_type": poll["poll_type"],
                    "voting_type": poll["voting_type"],
                    "status": poll["status"],
                    "options": options,
                    "total_votes": total_votes,
                    "created_at": poll["created_at"],
                    "winning_option_id": poll.get("winning_option_id"),
                    "confirmed_at": poll.get("confirmed_at")
                }
            })
        
        return {
            "type": "polls_list",
            "cards": poll_cards,
            "metadata": {
                "group_id": group_id,
                "total_polls": len(poll_cards),
                "status_filter": status,
                "type_filter": poll_type
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to get polls: {str(e)}",
                    "error_type": "database_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def confirm_poll_result(
    poll_id: str,
    group_id: str,
    confirmed_by: str,
    winning_option_id: str
) -> Dict[str, Any]:
    """
    Confirm the poll result and lock it in.
    AI calls this after user specifies which option to confirm.
    
    **When to use:**
    - User says: "Confirm option 1"
    - After majority is reached and user approves
    
    **Usage examples:**
    - User: "Confirm option 1" → confirm_poll_result(poll_id, group_id, user_id, winning_option_id)
    
    Args:
        poll_id: ID of the poll to confirm
        group_id: ID of the group
        confirmed_by: User ID who confirmed
        winning_option_id: The option ID to confirm as winner
        
    Returns:
        Confirmation card with locked result
    """
    try:
        # Get poll and option details
        poll = supabase.table("polls")\
            .select("*")\
            .eq("id", poll_id)\
            .single()\
            .execute().data
        
        if not poll:
            raise Exception("Poll not found")
        
        winner = supabase.table("poll_options")\
            .select("*")\
            .eq("id", winning_option_id)\
            .single()\
            .execute().data
        
        if not winner:
            raise Exception("Option not found")
        
        # Update poll status to 'confirmed'
        supabase.table("polls").update({
            "status": "confirmed",
            "winning_option_id": winner["id"],
            "confirmed_by": confirmed_by,
            "confirmed_at": datetime.now().isoformat()
        }).eq("id", poll_id).execute()
        
        # Update winning option
        supabase.table("poll_options").update({
            "is_winner": True
        }).eq("id", winner["id"]).execute()
        
        return {
            "type": "poll_confirmed",
            "cards": [
                {
                    "type": "confirmation",
                    "id": f"confirm_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": True,
                        "message": f"Confirmed! {winner['text']}",
                        "poll_id": poll_id,
                        "question": poll["question"],
                        "winner": winner,
                        "confirmed_at": datetime.now().isoformat()
                    }
                }
            ],
            "metadata": {
                "poll_id": poll_id,
                "winner_option_id": winner["id"],
                "winner_text": winner["text"],
                "action": "poll_locked"
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to confirm poll: {str(e)}",
                    "error_type": "database_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def cancel_poll(
    poll_id: str,
    group_id: str,
    cancelled_by: str
) -> Dict[str, Any]:
    """
    Cancel an active poll.
    AI calls this if users decide not to vote or want to restart.
    
    Args:
        poll_id: ID of the poll
        group_id: ID of the group
        cancelled_by: User ID who cancelled
        
    Returns:
        Confirmation card
    """
    try:
        supabase.table("polls").update({
            "status": "cancelled",
            "cancelled_by": cancelled_by,
            "cancelled_at": datetime.now().isoformat()
        }).eq("id", poll_id).execute()
        
        return {
            "type": "poll_cancelled",
            "cards": [
                {
                    "type": "confirmation",
                    "id": f"confirm_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": True,
                        "message": "Poll cancelled",
                        "poll_id": poll_id
                    }
                }
            ],
            "metadata": {
                "poll_id": poll_id,
                "action": "poll_cancelled"
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to cancel poll: {str(e)}",
                    "error_type": "database_error"
                }
            }],
            "metadata": {"error": str(e)}
        }

