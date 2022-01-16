from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

__all__ = [
    "Entity",
]


class Entity(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
