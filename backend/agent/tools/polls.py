"""
Poll Tools for Group Decision Making
"""
from typing import Dict, List, Any
import uuid
from datetime import datetime


def create_poll(
    group_id: str,
    question: str,
    options: List[str],
    poll_type: str = "single_choice",
    created_by: str = None
) -> Dict[str, Any]:
    """
    Create a voting poll for group decision making.
    Useful for letting group members vote on hotels, destinations, dates, activities, etc.
    
    Args:
        group_id: ID of the travel group
        question: The question to ask (e.g., "Which hotel should we book?")
        options: List of options to vote on (e.g., ["Hotel A", "Hotel B", "Hotel C"])
        poll_type: Type of poll - "single_choice" (one vote) or "multiple_choice" (multiple votes), default is "single_choice"
        created_by: User ID of poll creator (optional)
        
    Returns:
        Confirmation card with poll details and poll_id
    """
    # TODO: In production, save to database
    # INSERT INTO polls (poll_id, group_id, question, options, poll_type, created_by, created_at)
    
    # Generate poll ID
    poll_id = f"poll_{uuid.uuid4().hex[:12]}"
    
    # Create poll structure
    poll_data = {
        "poll_id": poll_id,
        "group_id": group_id,
        "question": question,
        "options": [
            {
                "option_id": f"opt_{i}",
                "text": option,
                "votes": 0,
                "voters": []
            }
            for i, option in enumerate(options)
        ],
        "poll_type": poll_type,
        "created_by": created_by,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "total_votes": 0
    }
    
    # Return confirmation card
    return {
        "type": "poll_result",
        "cards": [
            {
                "type": "confirmation",
                "id": f"confirm_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": True,
                    "message": f"Poll created successfully: '{question}'",
                    "poll_id": poll_id,
                    "question": question,
                    "options": options,
                    "poll_type": poll_type,
                    "action_required": "Group members can now vote on this poll"
                }
            }
        ],
        "metadata": {
            "poll_id": poll_id,
            "group_id": group_id,
            "total_options": len(options)
        }
    }


def vote_on_poll(
    poll_id: str,
    user_id: str,
    selected_options: List[str]
) -> Dict[str, Any]:
    """
    Cast a vote on an existing poll.
    
    Args:
        poll_id: ID of the poll to vote on
        user_id: ID of the user casting the vote
        selected_options: List of selected option texts (for single_choice, should have 1 item)
        
    Returns:
        Confirmation card with updated vote status
    """
    # TODO: In production, update database
    # UPDATE poll_options SET votes = votes + 1 WHERE poll_id = ? AND option_text = ?
    # INSERT INTO poll_votes (poll_id, user_id, option_id, voted_at)
    
    # Placeholder - simulate vote recording
    return {
        "type": "vote_result",
        "cards": [
            {
                "type": "confirmation",
                "id": f"confirm_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": True,
                    "message": "Your vote has been recorded",
                    "poll_id": poll_id,
                    "user_id": user_id,
                    "selected_options": selected_options,
                    "voted_at": datetime.now().isoformat()
                }
            }
        ],
        "metadata": {
            "poll_id": poll_id,
            "user_id": user_id
        }
    }


def get_poll_results(
    poll_id: str,
    group_id: str = None
) -> Dict[str, Any]:
    """
    Get current results of a poll including vote counts and percentages.
    
    Args:
        poll_id: ID of the poll to retrieve
        group_id: ID of the group (optional, for validation)
        
    Returns:
        Poll results card with vote counts, percentages, and current winner
    """
    # TODO: In production, fetch from database
    # SELECT * FROM polls WHERE poll_id = ?
    # SELECT option_id, COUNT(*) as votes FROM poll_votes WHERE poll_id = ? GROUP BY option_id
    
    # Placeholder - return mock poll results
    mock_results = {
        "poll_id": poll_id,
        "group_id": group_id or "test_group",
        "question": "Which hotel should we book for our Paris trip?",
        "poll_type": "single_choice",
        "status": "active",
        "created_at": "2025-11-08T10:00:00",
        "total_votes": 8,
        "total_members": 10,
        "participation_rate": 0.8,
        "options": [
            {
                "option_id": "opt_0",
                "text": "Hotel Le Marais ($120/night) - Central location, breakfast included",
                "votes": 5,
                "percentage": 62.5,
                "voters": ["Alice", "Bob", "Carol", "David", "Eve"]
            },
            {
                "option_id": "opt_1",
                "text": "Hotel Montmartre ($95/night) - Near Sacré-Cœur, cozy atmosphere",
                "votes": 2,
                "percentage": 25.0,
                "voters": ["Frank", "Grace"]
            },
            {
                "option_id": "opt_2",
                "text": "Hotel Latin Quarter ($150/night) - Luxury, spa included",
                "votes": 1,
                "percentage": 12.5,
                "voters": ["Henry"]
            }
        ],
        "winner": {
            "option_id": "opt_0",
            "text": "Hotel Le Marais ($120/night) - Central location, breakfast included",
            "votes": 5,
            "percentage": 62.5
        },
        "pending_voters": ["Ian", "Jane"]
    }
    
    # Return as a poll results card
    return {
        "type": "poll_results",
        "cards": [
            {
                "type": "poll",
                "id": poll_id,
                "data": mock_results
            }
        ],
        "metadata": {
            "poll_id": poll_id,
            "group_id": mock_results["group_id"],
            "status": mock_results["status"],
            "total_votes": mock_results["total_votes"]
        }
    }


def close_poll(
    poll_id: str,
    group_id: str
) -> Dict[str, Any]:
    """
    Close an active poll and finalize results.
    
    Args:
        poll_id: ID of the poll to close
        group_id: ID of the group (for validation)
        
    Returns:
        Confirmation card with final results
    """
    # TODO: In production, update database
    # UPDATE polls SET status = 'closed', closed_at = NOW() WHERE poll_id = ?
    
    # Get final results
    results = get_poll_results(poll_id, group_id)
    
    # Update confirmation message
    return {
        "type": "poll_closed_result",
        "cards": [
            {
                "type": "confirmation",
                "id": f"confirm_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": True,
                    "message": f"Poll closed successfully",
                    "poll_id": poll_id,
                    "final_winner": results["cards"][0]["data"]["winner"],
                    "total_votes": results["cards"][0]["data"]["total_votes"],
                    "closed_at": datetime.now().isoformat()
                }
            },
            # Include final results
            results["cards"][0]
        ],
        "metadata": {
            "poll_id": poll_id,
            "group_id": group_id,
            "status": "closed"
        }
    }


def list_active_polls(
    group_id: str
) -> Dict[str, Any]:
    """
    List all active polls for a group.
    
    Args:
        group_id: ID of the group
        
    Returns:
        List of active polls with basic information
    """
    # TODO: In production, fetch from database
    # SELECT * FROM polls WHERE group_id = ? AND status = 'active'
    
    # Placeholder - return mock active polls
    mock_polls = [
        {
            "poll_id": "poll_abc123",
            "question": "Which hotel should we book for our Paris trip?",
            "total_votes": 8,
            "total_options": 3,
            "created_at": "2025-11-08T10:00:00",
            "status": "active"
        },
        {
            "poll_id": "poll_def456",
            "question": "What time should we meet at the airport?",
            "total_votes": 5,
            "total_options": 4,
            "created_at": "2025-11-08T14:30:00",
            "status": "active"
        }
    ]
    
    return {
        "type": "polls_list_result",
        "cards": [
            {
                "type": "poll",
                "id": poll["poll_id"],
                "data": poll
            }
            for poll in mock_polls
        ],
        "metadata": {
            "group_id": group_id,
            "total_active_polls": len(mock_polls)
        }
    }
