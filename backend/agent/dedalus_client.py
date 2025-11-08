"""
Dedalus Client
Wrapper for Dedalus AI SDK to simplify usage across the application.
"""
import os
from typing import List, Callable, Optional, Any, Dict

from dedalus_labs import AsyncDedalus, DedalusRunner
from dedalus_labs.utils.streaming import stream_async
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DedalusClient:
    """
    High-level client for Dedalus AI interactions.
    Handles AsyncDedalus and DedalusRunner initialization.
    """
    
    def __init__(self):
        """Initialize the Dedalus client"""
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        
        # Get default model from environment
        self.default_model = os.getenv("DEDALUS_MODEL", "openai/gpt-4o")
    
    async def run(
        self,
        input: str,
        tools: Optional[List[Callable]] = None,
        mcp_servers: Optional[List[str]] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Any:
        """
        Run the Dedalus agent with the given input.
        
        Args:
            input: The user's input message or prompt
            tools: Optional list of Python functions to use as tools
            mcp_servers: Optional list of MCP server identifiers (e.g., "joerup/open-meteo-mcp")
            model: Optional model override (defaults to ANTHROPIC_MODEL from env)
            stream: Whether to stream the response
            
        Returns:
            DedalusRunner result object with final_output and tool_calls
        """
        if tools is None:
            tools = []
        
        if mcp_servers is None:
            mcp_servers = []
        
        # Use provided model or default
        model_to_use = model or self.default_model
        
        # Run the agent
        result = await self.runner.run(
            input=input,
            model=[model_to_use],
            tools=tools,
            mcp_servers=mcp_servers,
            stream=stream
        )
        
        return result
    
    async def run_with_streaming(
        self,
        input: str,
        tools: Optional[List[Callable]] = None,
        mcp_servers: Optional[List[str]] = None,
        model: Optional[str] = None
    ):
        """
        Run the agent with streaming enabled.
        Returns an async generator that yields chunks.
        
        Args:
            input: The user's input message or prompt
            tools: Optional list of Python functions to use as tools
            mcp_servers: Optional list of MCP server identifiers
            model: Optional model override
            
        Yields:
            Response chunks as they arrive
        """
        if tools is None:
            tools = []
        
        if mcp_servers is None:
            mcp_servers = []
        
        model_to_use = model or self.default_model
        
        result = await self.runner.run(
            input=input,
            model=[model_to_use],
            tools=tools,
            mcp_servers=mcp_servers,
            stream=True
        )
        
        # Stream the results
        async for chunk in stream_async(result):
            yield chunk


# Singleton instance
_dedalus_client = None


def get_dedalus_client() -> DedalusClient:
    """Get or create the singleton Dedalus client instance"""
    global _dedalus_client
    if _dedalus_client is None:
        _dedalus_client = DedalusClient()
    return _dedalus_client


