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


def get_poll_status(
    poll_id: str,
    group_id: str
) -> Dict[str, Any]:
    """
    Get current voting status and check if majority reached.
    Use this to monitor vote progress and detect when majority is reached.
    
    **When to use:**
    - User asks: "What's the poll status?"
    - User asks: "Who's winning?"
    - After poll creation to check if anyone voted
    - Periodically to detect when majority is reached
    
    **Usage examples:**
    - "Show me the hotel poll results" → get_poll_status(poll_id="poll_abc123", group_id=GROUP_ID)
    - "Has anyone voted yet?" → get_poll_status(poll_id="poll_xyz", group_id=GROUP_ID)
    - Check after creation: create_poll() → get_poll_status() to see current state
    
    Args:
        poll_id: ID of the poll (from create_poll result or previous context)
        group_id: ID of the travel group (from context)
        
    Returns:
        Poll status card with:
        - Current vote counts and percentages per option
        - Total votes and participation rate
        - Leader (winning option)
        - has_majority flag (true if winner has >50% of group members)
        - List of users who voted
    """
    try:
        # Get poll data
        poll = supabase.table("polls")\
            .select("*")\
            .eq("id", poll_id)\
            .single()\
            .execute().data
        
        if not poll:
            raise Exception("Poll not found")
        
        # Get options with vote counts
        options = supabase.table("poll_options")\
            .select("*")\
            .eq("poll_id", poll_id)\
            .order("order_index")\
            .execute().data
        
        # Get total group members
        members_count = supabase.table("group_members")\
            .select("id", count="exact")\
            .eq("group_id", group_id)\
            .execute().count or 0
        
        # Get who voted
        votes = supabase.table("poll_votes")\
            .select("user_id, option_id")\
            .eq("poll_id", poll_id)\
            .execute().data
        
        voted_users = list(set(v["user_id"] for v in votes))
        total_votes = len(voted_users)
        
        # Calculate percentages and find leader
        leader_option = None
        max_votes = 0
        
        for opt in options:
            opt_votes = len([v for v in votes if v["option_id"] == opt["id"]])
            opt["votes"] = opt_votes
            opt["percentage"] = (opt_votes / total_votes * 100) if total_votes > 0 else 0
            
            if opt_votes > max_votes:
                max_votes = opt_votes
                leader_option = opt
        
        # Check if majority reached (>50% of group members)
        majority_threshold = members_count / 2
        has_majority = max_votes > majority_threshold
        participation_rate = (total_votes / members_count) if members_count > 0 else 0
        
        return {
            "type": "poll_status",
            "cards": [
                {
                    "type": "poll",
                    "id": poll_id,
                    "data": {
                        "poll_id": poll_id,
                        "question": poll["question"],
                        "poll_type": poll["poll_type"],
                        "status": poll["status"],
                        "options": options,
                        "total_votes": total_votes,
                        "total_members": members_count,
                        "participation_rate": round(participation_rate * 100, 1),
                        "has_majority": has_majority,
                        "leader": leader_option,
                        "voted_users": voted_users
                    }
                }
            ],
            "metadata": {
                "poll_id": poll_id,
                "has_majority": has_majority,
                "should_ask_confirmation": has_majority and poll["status"] == "active"
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
                    "message": f"Failed to get poll status: {str(e)}",
                    "error_type": "database_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def confirm_poll_result(
    poll_id: str,
    group_id: str,
    confirmed_by: str,
    winning_option_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Confirm the poll result and lock it in.
    AI calls this after user says "confirm".
    
    Args:
        poll_id: ID of the poll
        group_id: ID of the group
        confirmed_by: User ID who confirmed
        winning_option_id: Specific option to confirm (if None, uses current leader)
        
    Returns:
        Confirmation card with locked result
    """
    try:
        # Get current poll status
        status_result = get_poll_status(poll_id, group_id)
        if status_result["type"] == "error_result":
            return status_result
        
        poll_data = status_result["cards"][0]["data"]
        
        # Determine winner
        if winning_option_id:
            winner = next((opt for opt in poll_data["options"] if opt["id"] == winning_option_id), None)
        else:
            winner = poll_data["leader"]
        
        if not winner:
            raise Exception("No winning option found")
        
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
                        "question": poll_data["question"],
                        "winner": winner,
                        "total_votes": poll_data["total_votes"],
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


def get_latest_poll(
    group_id: str,
    poll_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the most recent active poll for the group.
    Use this when user asks about "the poll" without specifying poll_id.
    
    **When to use:**
    - User: "Show me the poll results" (no specific poll_id mentioned)
    - User: "What's the voting status?" (refers to recent poll)
    - User: "Has anyone voted on the hotel poll?" (poll_type hint)
    - After creating a poll and user asks about it in next message
    
    **Usage examples:**
    - "Show me the poll" → get_latest_poll(group_id=GROUP_ID)
    - "Hotel poll results?" → get_latest_poll(group_id=GROUP_ID, poll_type="hotel")
    
    Args:
        group_id: ID of the travel group
        poll_type: Optional filter by type (hotel, restaurant, destination, etc.)
        
    Returns:
        Same format as get_poll_status() with latest poll data
    """
    try:
        # Query for latest active poll
        query = supabase.table("polls")\
            .select("*")\
            .eq("group_id", group_id)\
            .eq("status", "active")\
            .order("created_at", desc=True)
        
        if poll_type:
            query = query.eq("poll_type", poll_type)
        
        result = query.limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            return {
                "type": "error_result",
                "cards": [{
                    "type": "confirmation",
                    "id": f"error_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": False,
                        "message": "No active poll found for this group",
                        "error_type": "not_found"
                    }
                }],
                "metadata": {"error": "no_active_poll"}
            }
        
        poll = result.data[0]
        poll_id = poll["id"]
        
        # Use get_poll_status to get full details
        return get_poll_status(poll_id, group_id)
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to get latest poll: {str(e)}",
                    "error_type": "database_error"
                }
            }],
            "metadata": {"error": str(e)}
        }
