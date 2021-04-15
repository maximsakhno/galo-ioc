from typing import (
    Generic,
    Optional,
    Any,
    Type,
)
from dataclasses import (
    dataclass,
)
from .types import (
    F,
)


__all__ = [
    "Key",
]


@dataclass(frozen=True)
class Key(Generic[F]):
    factory_type: Type[F]
    id: Optional[Any] = None
