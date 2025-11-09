"""
Agent Runner
Manages Dedalus AI agent execution with tools and MCP servers.
"""
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from agent.dedalus_client import get_dedalus_client

# Import all tool functions
from agent.tools.budget import calculate_budget
from agent.tools.expenses import track_expense
from agent.tools.location import get_user_location, get_group_members_locations
from agent.tools.preferences import (
    get_user_preferences,
    get_all_group_preferences,
    update_user_preferences,
    get_group_preference_schema
)
from agent.tools.polls import (
    create_poll,
    get_group_polls,
    confirm_poll_result,
    cancel_poll
)
# Google Maps API (Places + Directions + Hotels)
from agent.tools.google_maps import (
    search_restaurants,
    search_attractions,
    search_hotels,
    search_transportation
)
# Kiwi.com flights via RapidAPI
#from agent.tools.kiwi_flights import search_flights_kiwi
# Booking.com API (Flights + Hotels with pricing)
from agent.tools.rapidapi_search import (
    search_flights_booking,
    #search_hotels_booking
)


class TravelAgentRunner:
    """
    Wrapper for DedalusRunner with travel-specific configuration.
    Manages tool calling, MCP servers, and context.
    """
    
    def __init__(self):
        # Get the Dedalus client
        self.dedalus = get_dedalus_client()
        
        # All available tools
        self.tools = [
            calculate_budget,
            track_expense,
            get_user_location,
            get_group_members_locations,
            get_user_preferences,
            get_all_group_preferences,
            update_user_preferences,
            get_group_preference_schema,
            create_poll,
            get_group_polls,
            confirm_poll_result,
            cancel_poll,
            # Google Maps API
            search_restaurants,
            search_attractions,
            search_hotels,  # Google Places hotels (basic info)
            search_transportation,
            # Booking.com flights
            search_flights_booking,
        ]
        
        # MCP servers for travel planning
        self.mcp_servers = [
            #"windsor/foursquare-places-mcp", # Search for places and place recommendations.
            "tsion/brave-search-mcp",        # Web search and local search with Brave.
            # "windsor/ticketmaster-mcp",      # Discover events, venues, and attractions through the Ticketmaster API.
            "akakak/sonar",                  # Web searches using Perplexity's Sonar Pro.
        ]
        
        # Get model from environment
        self.model = os.getenv("DEDALUS_MODEL", "openai/gpt-4.1")
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        self.domain_prompts = self._load_domain_prompts()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt from file"""
        # Try compact version first
        compact_path = Path(__file__).parent / "prompts" / "system_compact.txt"
        if compact_path.exists():
            with open(compact_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Fall back to full version
        prompt_path = Path(__file__).parent / "prompts" / "system_claude.txt"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Default prompt if file doesn't exist
        return """You are a helpful travel planning assistant for group trips.
You help groups coordinate travel plans, find accommodations, search flights,
manage budgets, and create itineraries based on their preferences."""
    
    def _load_domain_prompts(self) -> Dict[str, str]:
        """Load domain-specific prompts (flight, hotel, etc.)"""
        prompts_dir = Path(__file__).parent / "prompts"
        domain_prompts: Dict[str, str] = {}
        if prompts_dir.exists():
            for path in sorted(prompts_dir.glob("domain_*.txt")):
                key = path.stem.replace("domain_", "")
                with open(path, 'r', encoding='utf-8') as f:
                    domain_prompts[key] = f.read().strip()
        return domain_prompts
    
    async def chat(
        self,
        message: str,
        group_id: str,
        user_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Process a chat message with the AI agent.
        
        Args:
            message: The user's message
            group_id: ID of the group chat
            user_id: ID of the user sending the message
            user_preferences: Optional dict of user preferences
            chat_history: Optional list of previous messages
            stream: Whether to stream the response
            
        Returns:
            Dictionary with structured agent response (AgentResponse format)
        """
        # Build the full input with context
        full_input = self._build_input(
            message=message,
            group_id=group_id,
            user_id=user_id,
            user_preferences=user_preferences,
            chat_history=chat_history
        )
        
        # Run the agent using the Dedalus client
        result = await self.dedalus.run(
            input=full_input,
            tools=self.tools,
            mcp_servers=self.mcp_servers,
            model=self.model,
            stream=stream
        )
        
        # Extract cards from tool results
        cards = self._extract_cards_from_result(result)
        
        return {
            "group_id": group_id,
            "message": result.final_output,
            "cards": cards,
            "interactive_elements": [],
            "metadata": {
                "user_id": user_id,
                "tool_calls_count": len(result.tool_calls) if hasattr(result, 'tool_calls') else 0
            }
        }
    
    def _extract_cards_from_result(self, result: Any) -> List[Dict[str, Any]]:
        """
        Extract structured cards from the Dedalus result.
        Tool functions return data in format: {"type": "..._result", "cards": [...]}
        Dedalus wraps tool results as: [{"name": "tool_name", "result": {...}}]
        """
        cards = []
        
        # Check if result has tool_results attribute
        if hasattr(result, 'tool_results'):
            for tool_result in result.tool_results:
                # Tool result is a dict with 'name' and 'result' keys
                if isinstance(tool_result, dict):
                    # The actual result data is in the 'result' key
                    actual_result = tool_result.get('result', tool_result)
                    
                    # If it has a 'cards' key, extract them
                    if isinstance(actual_result, dict) and 'cards' in actual_result:
                        cards.extend(actual_result['cards'])
                        
                elif isinstance(tool_result, str):
                    # Try to parse as JSON (fallback)
                    try:
                        parsed = json.loads(tool_result)
                        actual_result = parsed.get('result', parsed)
                        if 'cards' in actual_result:
                            cards.extend(actual_result['cards'])
                    except json.JSONDecodeError:
                        pass
        
        return cards
    
    def _build_input(
        self,
        message: str,
        group_id: str,
        user_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build the full input prompt with context"""
        parts = [self.system_prompt, ""]
        
        # Add current date/time context (CRITICAL for date interpretation)
        current_date = datetime.now()
        parts.append("## Current Context:")
        parts.append(f"- CURRENT_DATE: {current_date.strftime('%Y-%m-%d')} ({current_date.strftime('%A, %B %d, %Y')})")
        parts.append(f"- CURRENT_TIME: {current_date.strftime('%H:%M:%S %Z')}")
        parts.append(f"- USER_ID: {user_id}")
        parts.append(f"- GROUP_ID: {group_id}")
        parts.append("")
        
        # Add user preferences if available
        if user_preferences:
            parts.append("## User Preferences:")
            for key, value in user_preferences.items():
                parts.append(f"- {key}: {value}")
            parts.append("")
        
        # Add recent chat history if available
        if chat_history:
            parts.append("## Recent Chat History:")
            for msg in chat_history[-10:]:  # Last 10 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"{role}: {content}")
            parts.append("")
        
        # Add current message
        parts.append("## Current Message:")
        parts.append(message)
        
        # Add domain playbooks for the LLM
        if self.domain_prompts:
            parts.append("## Domain Playbooks:")
            for key, content in self.domain_prompts.items():
                parts.append(f"### {key}")
                parts.append(content)
                parts.append("")
        
        return "\n".join(parts)


# Singleton instance
_travel_agent = None


def get_travel_agent() -> TravelAgentRunner:
    """Get or create the singleton travel agent instance"""
    global _travel_agent
    if _travel_agent is None:
        _travel_agent = TravelAgentRunner()
    return _travel_agent
