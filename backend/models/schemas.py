from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, condecimal, conint


# ============================================
# Agent Response Schemas (for structured cards)
# ============================================

class LocationData(BaseModel):
    """Geographic location information"""
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": x, "lng": y}


class HotelCardData(BaseModel):
    """Hotel/accommodation card data"""
    name: str
    rating: Optional[float] = None
    price_per_night: float
    currency: str = "USD"
    image_url: Optional[str] = None
    website: Optional[str] = None  # Hotel website URL
    amenities: List[str] = []
    location: Optional[LocationData] = None
    description: Optional[str] = None


class FlightCardData(BaseModel):
    """Flight card data"""
    airline: str
    flight_number: Optional[str] = None
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration_hours: float
    price_per_person: float
    total_price: float
    currency: str = "USD"
    stops: int = 0


class RestaurantCardData(BaseModel):
    """Restaurant card data"""
    name: str
    cuisine: Optional[str] = None
    rating: Optional[float] = None
    price_range: Optional[str] = None  # "$", "$$", "$$$", "$$$$"
    image_url: Optional[str] = None
    website: Optional[str] = None  # Restaurant website URL
    location: Optional[LocationData] = None
    description: Optional[str] = None


class AttractionCardData(BaseModel):
    """Tourist attraction card data"""
    name: str
    category: Optional[str] = None  # museum, park, landmark, etc.
    rating: Optional[float] = None
    price: Optional[float] = None
    currency: str = "USD"
    image_url: Optional[str] = None
    website: Optional[str] = None  # Attraction website URL
    location: Optional[LocationData] = None
    description: Optional[str] = None
    opening_hours: Optional[str] = None


class EventCardData(BaseModel):
    """Event card data"""
    name: str
    category: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    venue: Optional[str] = None
    location: Optional[LocationData] = None
    description: Optional[str] = None


class ItineraryDayData(BaseModel):
    """Single day in an itinerary"""
    day: int
    date: Optional[str] = None
    activities: List[Dict[str, Any]]  # [{time, activity, duration_hours, location}]


class ItineraryCardData(BaseModel):
    """Multi-day itinerary card data"""
    destination: str
    days: int
    daily_plans: List[ItineraryDayData]


class BudgetBreakdown(BaseModel):
    """Budget category breakdown"""
    flights: float
    accommodation: float
    food: float
    activities: float
    transportation: float
    miscellaneous: float
    total: float
    currency: str = "USD"


class BudgetCardData(BaseModel):
    """Budget planning card"""
    breakdown: BudgetBreakdown
    per_person: Optional[float] = None
    notes: Optional[str] = None


class MapCardData(BaseModel):
    """Map visualization card"""
    locations: List[LocationData]
    center: Optional[Dict[str, float]] = None  # {"lat": x, "lng": y}
    zoom_level: int = 10


class InteractiveElement(BaseModel):
    """Interactive UI elements (polls, buttons, etc.)"""
    type: Literal["poll", "button", "date_picker", "dropdown"]
    id: str
    label: str
    options: Optional[List[str]] = None  # For poll/dropdown
    action: Optional[str] = None  # API endpoint or callback


class AgentCard(BaseModel):
    """
    Generic card structure that can hold any type of structured data.
    The 'type' field determines which schema is used in 'data'.
    """
    card_id: str = Field(default_factory=lambda: f"card_{id(object())}")
    type: Literal[
        "hotel",
        "flight",
        "restaurant",
        "attraction",
        "event",
        "itinerary",
        "budget",
        "map",
        "confirmation",
        "generic",
        "preferences_result",
        "group_preferences_result",
        "update_result",
        "user_preferences",
        "location",
        "transportation"
    ]
    title: Optional[str] = None
    data: Dict[str, Any]


class AgentResponse(BaseModel):
    """
    Structured response from the AI agent.
    Includes both text message and structured cards for UI rendering.
    """
    message: str  # Human-readable text response
    cards: List[AgentCard] = []  # Structured data cards
    interactive_elements: List[InteractiveElement] = []  # Polls, buttons, etc.
    metadata: Optional[Dict[str, Any]] = None  # Extra context if needed


# ============================================
# Core Application Schemas
# ============================================

# --- Groups & Messages ---

class GroupCreate(BaseModel):
    name: str
    created_by: Optional[str] = None  # later connected to users table

class MessageCreate(BaseModel):
    group_id: str
    sender_id: str
    kind: Optional[str] = "text"
    content: str  # can hold {"text": "hello"} or more complex AI content
    body: Any

# --- Expense Splitting ---

class ExpenseParticipant(BaseModel):
    user_id: str
    share: Optional[condecimal(ge=0)] = None  # optional for equal split

class ExpenseCreate(BaseModel):
    group_id: str
    payer_id: str          # current user later (auth)
    description: Optional[str] = None
    amount: condecimal(ge=0)
    split_between: List[ExpenseParticipant]

# --- Polls (New System) ---

class PollOptionCreate(BaseModel):
    """Single option in a poll"""
    text: str
    metadata: Optional[Dict[str, Any]] = None  # Extra data (price, rating, etc.)

class PollCreate(BaseModel):
    """Create a new poll for group voting"""
    group_id: str
    created_by: str
    question: str
    options: List[PollOptionCreate]
    poll_type: Literal['destination', 'hotel', 'flight', 'restaurant', 'activity', 'date', 'time', 'custom'] = 'custom'
    voting_type: Literal['single_choice', 'multiple_choice'] = 'single_choice'
    expires_at: Optional[datetime] = None

class PollVote(BaseModel):
    """Cast a vote on a poll"""
    poll_id: str
    user_id: str
    option_ids: List[str]  # List of selected option IDs

class PollConfirm(BaseModel):
    """Confirm the winning option"""
    poll_id: str
    confirmed_by: str
    winning_option_id: str

# --- Old Poll System (to be deprecated) ---

class PollStart(BaseModel):
    group_id: str
    created_by: str
    mode: Literal['discover', 'fixed']
    days: Optional[conint(ge=1, le=30)] = None
    final_destination: Optional[str] = None  # required if mode='fixed'

class PreferenceCreate(BaseModel):
    poll_id: str
    user_id: str
    place_type: Optional[str] = None        # 'beach'|'mountain'|'city'|...
    budget: Optional[conint(ge=0)] = None   # per-person USD
    interests: Optional[List[str]] = None   # tags

class SuggestionItem(BaseModel):
    place_name: str
    reason: Optional[str] = None
    est_budget: Optional[int] = None
    activities: Optional[List[str]] = None
    fun_fact: Optional[str] = None

class PollSuggest(BaseModel):
    poll_id: str
    suggestions: List[SuggestionItem]

class VoteCreate(BaseModel):
    suggestion_id: str
    user_id: str
    vote: bool  # True=yes, False=no

class ConfirmChoice(BaseModel):
    poll_id: str
    suggestion_id: str
    confirmed_by: str
