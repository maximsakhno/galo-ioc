from pydantic import BaseModel

__all__ = [
    "CongratulationRequest",
]


class CongratulationRequest(BaseModel):
    name: str
