from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


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


class BudgetCardData(BaseModel):
    """Budget summary card data"""
    total_budget: float
    people: int
    duration_days: int
    per_person_budget: float
    per_day_budget: float
    breakdown: BudgetBreakdown
    currency: str = "USD"


class ExpenseCardData(BaseModel):
    """Expense tracking card data"""
    description: str
    amount: float
    paid_by: str
    timestamp: str
    currency: str = "USD"
    split_among: Optional[List[str]] = None


class DirectionsCardData(BaseModel):
    """Directions/route card data"""
    origin: str
    destination: str
    waypoints: List[str] = []
    mode: str = "driving"
    total_distance_km: float
    estimated_duration_minutes: int
    steps: List[Dict[str, Any]]


class UserLocationCardData(BaseModel):
    """User location card data"""
    user_id: str
    user_name: Optional[str] = None
    city: str
    state: Optional[str] = None
    country: str
    country_code: Optional[str] = None
    coordinates: Dict[str, float]  # {"lat": x, "lng": y}
    timezone: Optional[str] = None
    last_updated: Optional[str] = None


class UserPreferencesCardData(BaseModel):
    """User travel preferences card data"""
    user_id: str
    user_name: Optional[str] = None
    group_id: str
    departure_city: Optional[str] = None
    budget_max: Optional[float] = None
    budget_range: Optional[str] = None  # low, medium, high
    interests: Optional[List[str]] = []
    dietary_restrictions: Optional[List[str]] = []
    accommodation_preference: Optional[str] = None
    travel_pace: Optional[str] = None
    available_dates: Optional[Dict[str, str]] = None  # {"start": "...", "end": "..."}
    # Extensible for custom fields
    custom_fields: Optional[Dict[str, Any]] = None


class GroupConsensusCardData(BaseModel):
    """Group consensus summary card data"""
    group_id: str
    total_members: int
    budget_range: Dict[str, float]  # {"min": x, "max": y, "average": z}
    common_interests: List[str]
    overlapping_dates: Optional[Dict[str, str]] = None
    departure_cities: List[str]
    dietary_restrictions: List[str]


class ConfirmationCardData(BaseModel):
    """Generic confirmation card data"""
    success: bool
    message: str
    updated_fields: Optional[List[str]] = None
    user_id: Optional[str] = None
    group_id: Optional[str] = None


class PollOptionData(BaseModel):
    """Single option in a poll"""
    option_id: str
    text: str
    votes: int
    percentage: Optional[float] = None
    voters: Optional[List[str]] = []


class PollCardData(BaseModel):
    """Poll/voting card data"""
    poll_id: str
    group_id: str
    question: str
    poll_type: str  # "single_choice" or "multiple_choice"
    status: str  # "active" or "closed"
    options: List[PollOptionData]
    total_votes: int
    total_members: Optional[int] = None
    participation_rate: Optional[float] = None
    winner: Optional[PollOptionData] = None
    pending_voters: Optional[List[str]] = []
    created_at: Optional[str] = None
    closed_at: Optional[str] = None


class AgentCard(BaseModel):
    """
    A structured card that can be rendered in the UI.
    Type determines which component to use for rendering.
    """
    type: Literal[
        "hotel", "flight", "restaurant", "attraction", 
        "event", "itinerary", "budget", "expense", "directions", "location",
        "user_preferences", "group_consensus", "confirmation", "preference_schema", "poll"
    ]
    id: str
    data: Dict[str, Any]  # Will match one of the *CardData schemas above


class InteractiveElement(BaseModel):
    """Interactive elements like polls or action buttons"""
    type: Literal["poll", "button", "selection"]
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
# Existing Schemas
# ============================================

class Group(BaseModel):
    id: str
    name: str


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1)


class Message(BaseModel):
    id: str
    group_id: str
    sender: str
    content: str
    created_at: Optional[datetime] = None


class MessageCreate(BaseModel):
    group_id: str
    sender: str
    content: str


class Poll(BaseModel):
    id: str
    group_id: str
    question: str
    options: List[str]
    votes: Dict[str, int] = {}


class PollCreate(BaseModel):
    group_id: str
    question: str
    options: List[str]


