from typing import Dict, Any
import uuid
from datetime import datetime


def track_expense(description: str, amount: float, paid_by: str) -> Dict[str, Any]:
    """
    Record a group expense for later reconciliation.
    
    Args:
        description: Description of the expense (e.g., "Dinner at restaurant")
        amount: Amount in USD
        paid_by: Name or ID of the person who paid
        
    Returns:
        Dictionary confirming the expense was tracked in card format
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    return {
        "type": "expense_result",
        "cards": [
            {
                "type": "expense",
                "id": f"expense_{uuid.uuid4().hex[:8]}",
                "data": {
                    "description": description,
                    "amount": amount,
                    "paid_by": paid_by,
                    "timestamp": timestamp,
                    "currency": "USD"
                }
            }
        ],
        "metadata": {
            "saved": True
        }
    }


