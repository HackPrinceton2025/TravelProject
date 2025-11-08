from typing import Any
from utils.supabase_client import get_supabase_client


def get_db() -> Any:
    """
    Placeholder database dependency. Returns Supabase client if configured.
    """
    return get_supabase_client()


