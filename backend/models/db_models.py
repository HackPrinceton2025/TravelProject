"""
Placeholder DB models. Replace with ORM models (e.g., SQLAlchemy) or Supabase tables.
"""

from dataclasses import dataclass


@dataclass
class DBGroup:
    id: str
    name: str


@dataclass
class DBMessage:
    id: str
    group_id: str
    sender: str
    content: str


