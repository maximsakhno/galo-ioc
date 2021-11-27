from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


__all__ = [
    "Entity",
]


class Entity(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
