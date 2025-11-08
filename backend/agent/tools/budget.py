from typing import Dict, Any
import uuid


def calculate_budget(total_budget: float, people: int, duration_days: int) -> Dict[str, Any]:
    """
    Compute budget allocation across flights, stays, food, and activities.
    
    Args:
        total_budget: Total budget available for the trip in USD
        people: Number of people in the group
        duration_days: Duration of the trip in days
        
    Returns:
        Dictionary with budget breakdown in card format
    """
    # Suggested allocation percentages
    per_person_budget = total_budget / people
    
    breakdown = {
        "flights": total_budget * 0.35,
        "accommodation": total_budget * 0.30,
        "food": total_budget * 0.20,
        "activities": total_budget * 0.15
    }
    
    # Return in card format
    return {
        "type": "budget_result",
        "cards": [
            {
                "type": "budget",
                "id": f"budget_{uuid.uuid4().hex[:8]}",
                "data": {
                    "total_budget": total_budget,
                    "people": people,
                    "duration_days": duration_days,
                    "per_person_budget": per_person_budget,
                    "per_day_budget": total_budget / duration_days,
                    "breakdown": breakdown,
                    "currency": "USD"
                }
            }
        ]
    }


