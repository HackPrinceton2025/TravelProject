from typing import Dict, Any, List, Optional
import uuid


# Predefined options for common preference fields
PREDEFINED_INTERESTS = [
    "Museums", "Food & Dining", "Nightlife", "Shopping",
    "Nature & Hiking", "Beach", "Adventure Sports", "Cultural Sites",
    "Photography", "History", "Art & Galleries", "Local Markets",
    "Architecture", "Music & Concerts", "Relaxation & Spa", "Wildlife"
]

PREDEFINED_DIETARY = [
    "Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher",
    "Dairy-Free", "Nut Allergy", "Seafood Allergy", "No Pork", 
    "No Beef", "Pescatarian", "Keto", "Paleo"
]

PREDEFINED_TRAVEL_PACE = [
    "Fast-Paced",      # Multiple activities per day, early starts, packed schedule
    "Moderate",        # Balanced mix of activities and rest
    "Relaxed",         # Leisurely pace, plenty of downtime
    "Flexible"         # No fixed schedule, go with the flow
]


def normalize_preference_list(
    items: List[str],
    predefined_options: List[str]
) -> List[str]:
    """
    Normalize a list of preference items.
    Predefined items stay as-is, custom items get 'Custom:' prefix.
    
    Args:
        items: List of items to normalize
        predefined_options: List of predefined valid options
        
    Returns:
        Normalized list with custom items prefixed
    """
    normalized = []
    for item in items:
        item = item.strip()
        if not item:
            continue
            
        # Check if it's already a custom item
        if item.startswith("Custom:"):
            normalized.append(item)
        # Check if it's in predefined options
        elif item in predefined_options:
            normalized.append(item)
        else:
            # Convert to custom item
            normalized.append(f"Custom: {item}")
    
    return normalized


def get_user_preferences(user_id: str, group_id: str) -> Dict[str, Any]:
    """
    Get user's travel preferences for a specific group.
    Preferences are customizable per group based on the trip type.
    
    Args:
        user_id: ID of the user
        group_id: ID of the group (preferences can vary by group)
        
    Returns:
        Dictionary with user preferences in card format
    """
    # TODO: In production, fetch from database
    # SELECT * FROM user_preferences WHERE user_id = ? AND group_id = ?
    
    # Placeholder implementation - return mock preferences
    # The schema is flexible - groups can define which fields they track
    preferences_data = {
        "user_id": user_id,
        "group_id": group_id,
        
        # Standard fields (commonly used)
        "departure_city": "New York",
        "budget_range": "medium",  # low, medium, high
        "budget_max": 3000,  # USD
        
        # Custom fields (defined by group creator)
        "interests": ["Museums", "Food & Dining", "Custom: Wine Tasting"],
        "dietary_restrictions": ["Vegetarian"],
        "accommodation_preference": "hotel",  # hotel, hostel, airbnb
        "travel_pace": "Moderate",
        
        # Optional fields
        "available_dates": {
            "start": "2025-12-01",
            "end": "2025-12-15"
        },
        "preferred_airlines": [],
        "loyalty_programs": {
            "marriott": "member_123",
            "united": "UA456789"
        }
    }
    
    # Return as a preference card
    return {
        "type": "preferences_result",
        "cards": [
            {
                "type": "user_preferences",
                "id": f"prefs_{uuid.uuid4().hex[:8]}",
                "data": preferences_data
            }
        ],
        "metadata": {
            "user_id": user_id,
            "group_id": group_id
        }
    }


def get_all_group_preferences(group_id: str) -> Dict[str, Any]:
    """
    Get travel preferences for all members in a group.
    Useful for finding consensus and planning together.
    
    Args:
        group_id: ID of the travel group
        
    Returns:
        Dictionary with all members' preferences in card format
    """
    # TODO: In production, fetch from database
    # SELECT * FROM user_preferences WHERE group_id = ?
    
    # Placeholder - return mock data for multiple users
    members_preferences = [
        {
            "user_id": "user_1",
            "user_name": "Alice",
            "departure_city": "New York",
            "budget_max": 3000,
            "interests": ["Museums", "Food & Dining", "Custom: Wine Tasting"],
            "dietary_restrictions": ["Vegetarian"],
            "travel_pace": "Moderate",
            "available_dates": {"start": "2025-12-01", "end": "2025-12-15"}
        },
        {
            "user_id": "user_2",
            "user_name": "Bob",
            "departure_city": "Boston",
            "budget_max": 2500,
            "interests": ["Nature & Hiking", "Photography"],
            "dietary_restrictions": [],
            "travel_pace": "Fast-Paced",
            "available_dates": {"start": "2025-12-05", "end": "2025-12-20"}
        },
        {
            "user_id": "user_3",
            "user_name": "Carol",
            "departure_city": "Philadelphia",
            "budget_max": 4000,
            "interests": ["Food & Dining", "Shopping", "Museums"],
            "dietary_restrictions": ["Gluten-Free", "Custom: Low Sodium"],
            "travel_pace": "Relaxed",
            "available_dates": {"start": "2025-12-01", "end": "2025-12-10"}
        }
    ]
    
    # Create a card for each member's preferences
    preference_cards = []
    for prefs in members_preferences:
        preference_cards.append({
            "type": "user_preferences",
            "id": f"prefs_{uuid.uuid4().hex[:8]}",
            "data": prefs
        })
    
    # Also create a summary card with consensus data
    # Calculate consensus - only count predefined options, not custom ones
    all_interests = []
    all_dietary = []
    all_travel_pace = []
    
    for pref in members_preferences:
        # Filter out custom items (with "Custom:" prefix) for consensus calculation
        interests = [item for item in pref.get("interests", []) if not item.startswith("Custom:")]
        dietary = [item for item in pref.get("dietary_restrictions", []) if not item.startswith("Custom:")]
        travel_pace = pref.get("travel_pace", "")
        
        all_interests.extend(interests)
        all_dietary.extend(dietary)
        if travel_pace and not travel_pace.startswith("Custom:"):
            all_travel_pace.append(travel_pace)
    
    # Find common items (appear more than once)
    from collections import Counter
    interest_counts = Counter(all_interests)
    dietary_counts = Counter(all_dietary)
    travel_pace_counts = Counter(all_travel_pace)
    
    common_interests = [item for item, count in interest_counts.items() if count > 1]
    common_dietary = [item for item, count in dietary_counts.items() if count > 1]
    most_common_pace = travel_pace_counts.most_common(1)[0][0] if travel_pace_counts else "Moderate"
    
    summary_card = {
        "type": "group_consensus",
        "id": f"consensus_{uuid.uuid4().hex[:8]}",
        "data": {
            "group_id": group_id,
            "total_members": len(members_preferences),
            "budget_range": {
                "min": min(p["budget_max"] for p in members_preferences),
                "max": max(p["budget_max"] for p in members_preferences),
                "average": sum(p["budget_max"] for p in members_preferences) / len(members_preferences)
            },
            "common_interests": common_interests,
            "overlapping_dates": {
                "start": "2025-12-05",  # Latest start date
                "end": "2025-12-10"     # Earliest end date
            },
            "departure_cities": ["New York", "Boston", "Philadelphia"],
            "dietary_restrictions": common_dietary,
            "preferred_travel_pace": most_common_pace
        }
    }
    
    preference_cards.append(summary_card)
    
    return {
        "type": "group_preferences_result",
        "cards": preference_cards,
        "metadata": {
            "group_id": group_id,
            "member_count": len(members_preferences)
        }
    }


def update_user_preferences(
    user_id: str,
    group_id: str,
    departure_city: str = None,
    budget_max: int = None,
    interests: List[str] = None,
    dietary_restrictions: List[str] = None,
    travel_pace: str = None,
    available_dates_start: str = None,
    available_dates_end: str = None,
    custom_fields: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Update user's travel preferences for a specific group.
    Only provided fields will be updated.
    
    Args:
        user_id: ID of the user
        group_id: ID of the group
        departure_city: User's departure city (optional)
        budget_max: Maximum budget in USD (optional)
        interests: List of interests (can include predefined options or custom items, optional)
        dietary_restrictions: List of dietary restrictions (can include predefined or custom, optional)
        travel_pace: Preferred travel pace (e.g., "Fast-Paced", "Moderate", "Relaxed", optional)
        available_dates_start: Start date in YYYY-MM-DD format (optional)
        available_dates_end: End date in YYYY-MM-DD format (optional)
        custom_fields: Dictionary of custom preference fields defined by the group (e.g., {"accommodation_style": "luxury", "group_size_preference": "small"}, optional)
        
    Returns:
        Confirmation with updated preferences
    """
    # TODO: In production, update database
    # UPDATE user_preferences SET ... WHERE user_id = ? AND group_id = ?
    
    # Build preferences dictionary from provided arguments
    updated_prefs = {}
    
    if departure_city is not None:
        updated_prefs["departure_city"] = departure_city
    
    if budget_max is not None:
        updated_prefs["budget_max"] = budget_max
    
    # Normalize preference lists before saving
    if interests is not None:
        updated_prefs["interests"] = normalize_preference_list(
            interests, 
            PREDEFINED_INTERESTS
        )
    
    if dietary_restrictions is not None:
        updated_prefs["dietary_restrictions"] = normalize_preference_list(
            dietary_restrictions,
            PREDEFINED_DIETARY
        )
    
    if travel_pace is not None:
        pace_list = [travel_pace] if isinstance(travel_pace, str) else travel_pace
        normalized_pace = normalize_preference_list(pace_list, PREDEFINED_TRAVEL_PACE)
        updated_prefs["travel_pace"] = normalized_pace[0] if normalized_pace else "Moderate"
    
    if available_dates_start is not None or available_dates_end is not None:
        updated_prefs["available_dates"] = {}
        if available_dates_start:
            updated_prefs["available_dates"]["start"] = available_dates_start
        if available_dates_end:
            updated_prefs["available_dates"]["end"] = available_dates_end
    
    # Add custom fields directly without normalization
    if custom_fields is not None:
        for field_name, field_value in custom_fields.items():
            updated_prefs[field_name] = field_value
    
    # Placeholder - simulate update
    return {
        "type": "update_result",
        "cards": [
            {
                "type": "confirmation",
                "id": f"confirm_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": True,
                    "message": "Preferences updated successfully",
                    "updated_fields": list(updated_prefs.keys()),
                    "user_id": user_id,
                    "group_id": group_id,
                    "updated_preferences": updated_prefs
                }
            }
        ],
        "metadata": {
            "updated_preferences": updated_prefs
        }
    }


def get_group_preference_schema(group_id: str) -> Dict[str, Any]:
    """
    Get the preference schema (fields) defined for this group.
    Group creators can customize which fields to track.
    
    Args:
        group_id: ID of the group
        
    Returns:
        Schema definition with field types and requirements
    """
    # TODO: In production, fetch from database
    # SELECT preference_schema FROM groups WHERE group_id = ?
    
    # Placeholder - return a customizable schema
    schema = {
        "group_id": group_id,
        "required_fields": [
            {
                "name": "departure_city",
                "type": "string",
                "label": "Departure City",
                "description": "City you'll be traveling from"
            },
            {
                "name": "budget_max",
                "type": "number",
                "label": "Maximum Budget (USD)",
                "description": "Your maximum budget for this trip"
            },
            {
                "name": "available_dates",
                "type": "date_range",
                "label": "Available Dates",
                "description": "When are you available to travel?"
            }
        ],
        "optional_fields": [
            {
                "name": "interests",
                "type": "array",
                "label": "Interests",
                "description": "What are you interested in doing?",
                "options": ["food", "culture", "nature", "shopping", "adventure", "nightlife"]
            },
            {
                "name": "dietary_restrictions",
                "type": "array",
                "label": "Dietary Restrictions",
                "description": "Any dietary restrictions?"
            },
            {
                "name": "accommodation_preference",
                "type": "select",
                "label": "Accommodation Preference",
                "options": ["hotel", "hostel", "airbnb", "resort"]
            },
            {
                "name": "travel_pace",
                "type": "select",
                "label": "Travel Pace",
                "options": ["fast", "moderate", "relaxed"]
            }
        ]
    }
    
    return {
        "type": "schema_result",
        "cards": [
            {
                "type": "preference_schema",
                "id": f"schema_{uuid.uuid4().hex[:8]}",
                "data": schema
            }
        ]
    }
