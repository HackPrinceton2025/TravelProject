import os
from typing import Any, Optional

try:
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None  # type: ignore


def get_supabase_client() -> Optional[Any]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key or create_client is None:
        return None
    return create_client(url, key)


