from typing import Dict, Any, List, Optional
import uuid
from utils.supabase_client import supabase


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


def check_user_has_preferences(user_id: str, group_id: str) -> bool:
    """
    Quick check if user has set any preferences for this group.
    Used by the agent to determine if it should guide the user through preference setup.
    
    Args:
        user_id: ID of the user
        group_id: ID of the group
        
    Returns:
        True if preferences exist, False otherwise
    """
    try:
        response = supabase.table("user_preferences")\
            .select("id")\
            .eq("user_id", user_id)\
            .eq("group_id", group_id)\
            .execute()
        
        return bool(response.data)
    except:
        return False


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
    try:
        # Fetch from Supabase user_preferences table
        response = supabase.table("user_preferences")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("group_id", group_id)\
            .single()\
            .execute()
        
        if response.data:
            preferences_data = response.data
            
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
        else:
            # No preferences found - return empty/default
            return {
                "type": "preferences_result",
                "cards": [
                    {
                        "type": "user_preferences",
                        "id": f"prefs_{uuid.uuid4().hex[:8]}",
                        "data": {
                            "user_id": user_id,
                            "group_id": group_id,
                            "message": "No preferences set yet. Please update your preferences."
                        }
                    }
                ],
                "metadata": {
                    "user_id": user_id,
                    "group_id": group_id,
                    "preferences_exist": False
                }
            }
    
    except Exception as e:
        # Error querying database
        return {
            "type": "error_result",
            "cards": [
                {
                    "type": "confirmation",
                    "id": f"error_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": False,
                        "message": f"Failed to fetch preferences: {str(e)}",
                        "error_type": "database_error"
                    }
                }
            ],
            "metadata": {
                "error": str(e)
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
    try:
        # Fetch all preferences for this group from Supabase
        response = supabase.table("user_preferences")\
            .select("*, users(id, name)")\
            .eq("group_id", group_id)\
            .execute()
        
        if not response.data:
            return {
                "type": "group_preferences_result",
                "cards": [
                    {
                        "type": "confirmation",
                        "id": f"info_{uuid.uuid4().hex[:8]}",
                        "data": {
                            "success": True,
                            "message": "No group members have set preferences yet.",
                            "group_id": group_id
                        }
                    }
                ],
                "metadata": {
                    "group_id": group_id,
                    "member_count": 0
                }
            }
        
        # Extract preferences data
        members_preferences = []
        for row in response.data:
            pref_data = dict(row)
            # Add user name from joined users table if available
            if "users" in pref_data and pref_data["users"]:
                pref_data["user_name"] = pref_data["users"].get("name", "Unknown")
                del pref_data["users"]  # Remove nested object
            members_preferences.append(pref_data)
        
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
        
        # Calculate budget range and dates if available
        budget_range = {}
        if members_preferences and any("budget_max" in p for p in members_preferences):
            budgets = [p.get("budget_max", 0) for p in members_preferences if p.get("budget_max")]
            if budgets:
                budget_range = {
                    "min": min(budgets),
                    "max": max(budgets),
                    "average": sum(budgets) / len(budgets)
                }
        
        summary_card = {
            "type": "group_consensus",
            "id": f"consensus_{uuid.uuid4().hex[:8]}",
            "data": {
                "group_id": group_id,
                "total_members": len(members_preferences),
                "budget_range": budget_range,
                "common_interests": common_interests,
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
    
    except Exception as e:
        # Error querying database
        return {
            "type": "error_result",
            "cards": [
                {
                    "type": "confirmation",
                    "id": f"error_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": False,
                        "message": f"Failed to fetch group preferences: {str(e)}",
                        "error_type": "database_error"
                    }
                }
            ],
            "metadata": {
                "error": str(e)
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
    This function performs an "upsert" - it will INSERT if preferences don't exist, or UPDATE if they do.
    Only provided fields will be updated (partial updates supported).
    
    **First-time users**: This function automatically creates a new preference entry if none exists.
    
    **Usage examples from chat**:
    - User: "My budget is $3000" → update_user_preferences(user_id, group_id, budget_max=3000)
    - User: "I'm vegetarian" → update_user_preferences(user_id, group_id, dietary_restrictions=["Vegetarian"])
    - User: "I like museums and food" → update_user_preferences(user_id, group_id, interests=["Museums", "Food & Dining"])
    - User: "I'm departing from Seoul" → update_user_preferences(user_id, group_id, departure_city="Seoul")
    
    Args:
        user_id: ID of the user (required, from context)
        group_id: ID of the group (required, from context)
        departure_city: User's departure city (optional, e.g., "New York", "Seoul")
        budget_max: Maximum budget in USD (optional, e.g., 3000)
        interests: List of interests - use predefined options when possible: "Museums", "Food & Dining", "Nature & Hiking", "Shopping", etc. Custom items will be prefixed with "Custom:" (optional)
        dietary_restrictions: List of dietary restrictions - use predefined: "Vegetarian", "Vegan", "Gluten-Free", "Halal", etc. Custom items prefixed with "Custom:" (optional)
        travel_pace: Preferred travel pace - "Fast-Paced", "Moderate", "Relaxed", or "Flexible" (optional)
        available_dates_start: Start date in YYYY-MM-DD format (optional)
        available_dates_end: End date in YYYY-MM-DD format (optional)
        custom_fields: Dictionary of custom preference fields (optional, e.g., {"accommodation_style": "luxury"})
        
    Returns:
        Confirmation card with success status and updated fields
    """
    try:
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
        
        # Check if preferences exist
        existing = supabase.table("user_preferences")\
            .select("id")\
            .eq("user_id", user_id)\
            .eq("group_id", group_id)\
            .execute()
        
        if existing.data:
            # Update existing preferences
            response = supabase.table("user_preferences")\
                .update(updated_prefs)\
                .eq("user_id", user_id)\
                .eq("group_id", group_id)\
                .execute()
        else:
            # Insert new preferences
            updated_prefs["user_id"] = user_id
            updated_prefs["group_id"] = group_id
            response = supabase.table("user_preferences")\
                .insert(updated_prefs)\
                .execute()
        
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
    
    except Exception as e:
        # Error updating database
        return {
            "type": "error_result",
            "cards": [
                {
                    "type": "confirmation",
                    "id": f"error_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": False,
                        "message": f"Failed to update preferences: {str(e)}",
                        "error_type": "database_error"
                    }
                }
            ],
            "metadata": {
                "error": str(e)
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
