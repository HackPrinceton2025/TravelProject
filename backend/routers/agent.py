from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.runner import get_travel_agent
from models.schemas import AgentResponse, AgentCard, InteractiveElement

router = APIRouter(tags=["agent"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    user_id: str  # ID of the user sending the message
    group_id: str  # ID of the group chat
    user_preferences: Optional[Dict[str, Any]] = None  # User's travel preferences
    chat_history: Optional[List[Dict[str, Any]]] = None  # Previous conversation
    stream: bool = False  # Whether to stream the response
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Find me hotels in Paris for next weekend under $200/night",
                "user_id": "user_123",
                "group_id": "group_456",
                "user_preferences": {
                    "budget_level": "moderate",
                    "accommodation_type": "hotel",
                    "dietary_restrictions": ["vegetarian"]
                },
                "chat_history": [
                    {"role": "user", "content": "We're planning a trip to Paris"},
                    {"role": "assistant", "content": "Great! I can help you plan your Paris trip. When are you planning to go?"}
                ],
                "stream": False
            }
        }


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(payload: ChatRequest) -> AgentResponse:
    """
    Chat with the AI travel agent.
    
    The agent has access to tools for:
    - **Search**: Flights, hotels, restaurants, attractions, transportation
    - **Planning**: Budget calculation, itinerary generation
    - **Group**: Polls, preferences, location tracking
    - **Expenses**: Track spending, split costs
    
    Returns structured response with:
    - **message**: Human-readable text response
    - **cards**: Structured data cards for UI rendering (hotels, flights, restaurants, etc.)
    - **interactive_elements**: Polls, buttons, voting options
    
    Args:
        payload: Chat request with:
            - message: User's message/query
            - user_id: ID of the user sending the message
            - group_id: ID of the group chat
            - user_preferences: Optional dict of user preferences (budget, dietary, etc.)
            - chat_history: Optional list of previous messages for context
            - stream: Whether to stream the response (default: False)
        
    Returns:
        AgentResponse with message, cards, and interactive elements
        
    Raises:
        HTTPException: 400 for invalid input, 500 for agent errors
    """
    try:
        # Validate input
        if not payload.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        if not payload.user_id or not payload.group_id:
            raise HTTPException(
                status_code=400,
                detail="Both user_id and group_id are required"
            )
        
        # Get agent instance
        agent = get_travel_agent()
        
        # Run agent with context
        result = await agent.chat(
            message=payload.message,
            group_id=payload.group_id,
            user_id=payload.user_id,  # Pass user_id to agent
            user_preferences=payload.user_preferences,
            chat_history=payload.chat_history,
            stream=payload.stream
        )
        
        return AgentResponse(**result)
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Agent error for user {payload.user_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {str(e)}"
        )


