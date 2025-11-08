from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.runner import get_travel_agent
from models.schemas import AgentResponse, AgentCard, InteractiveElement

router = APIRouter(tags=["agent"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    group_id: str
    user_preferences: Optional[Dict[str, Any]] = None
    chat_history: Optional[List[Dict[str, Any]]] = None
    stream: bool = False


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(payload: ChatRequest) -> AgentResponse:
    """
    Chat with the AI travel agent.
    
    The agent has access to tools for:
    - Budget calculation
    - Flight search
    - Accommodation search
    - Itinerary generation
    - Route directions
    - Expense tracking
    
    Returns structured response with:
    - message: Human-readable text
    - cards: Structured data cards for UI rendering (hotels, flights, etc.)
    - interactive_elements: Polls, buttons, etc.
    
    Args:
        payload: Chat request with message, group_id, and optional context
        
    Returns:
        Structured agent response with cards
    """
    try:
        agent = get_travel_agent()
        
        result = await agent.chat(
            message=payload.message,
            group_id=payload.group_id,
            user_preferences=payload.user_preferences,
            chat_history=payload.chat_history,
            stream=payload.stream
        )
        
        return AgentResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


