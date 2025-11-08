import os
from typing import Any, Dict, List

import requests
from fastapi import APIRouter

router = APIRouter(tags=["agent"])


@router.post("/chat")
def chat_with_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forwards a minimal request to a Dedalus-compatible API.
    Expected payload: {"messages": [...], "tools": [...]}
    """
    base = os.getenv("DEDALUS_API_BASE", "")
    key = os.getenv("DEDALUS_API_KEY", "")
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet")

    if not base or not key:
        return {"error": "Agent API is not configured"}

    headers = {"Authorization": f"Bearer {key}"}
    data = {
        "model": model,
        "messages": payload.get("messages", []),
        "tools": payload.get("tools", []),
    }
    r = requests.post(f"{base}/v1/chat/completions", headers=headers, json=data, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"status_code": r.status_code, "text": r.text}


