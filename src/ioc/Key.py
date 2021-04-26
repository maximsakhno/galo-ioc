from typing import (
    TypeVar,
    Optional,
    Any,
    Tuple,
    Type,
)
from .types import (
    F,
)


__all__ = [
    "Key",
]


K = TypeVar("K")


class Key(Tuple[Type[F], Optional[Any]]):
    def __new__(cls: Type[K], factory_type: Type[F], id: Optional[Any] = None) -> K:
        return super().__new__(cls, (factory_type, id))

    @property
    def factory_type(self) -> Type[F]:
        return self[0]

    @property
    def id(self) -> Optional[Any]:
        return self[1]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(factory_type={self.factory_type!r}, id={self.id!r})"
