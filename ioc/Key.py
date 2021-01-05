from typing import (
    TypeVar,
    Generic,
    Final,
    Optional,
    Any,
    Callable,
    Type,
)


__all__ = [
    "Key",
]


F = TypeVar("F", bound=Callable)


class Key(Generic[F]):
    factory_type: Final[Type[F]]
    id: Final[Optional[Any]]

    def __init__(self, factory_type: Type[F], id: Optional[Any] = None) -> None:
        self.factory_type = factory_type
        self.id = id

    def __eq__(self, other: Any) -> bool:
        return self is other or \
               isinstance(other, Key) and \
               self.factory_type == other.factory_type and \
               self.id == other.id

    def __hash__(self) -> int:
        return hash((self.factory_type, self.id))

    def __repr__(self) -> str:
        if self.id is None:
            return f"{self.__class__.__name__}(" \
                   f"factory_type={self.factory_type!r})"
        else:
            return f"{self.__class__.__name__}(" \
                   f"factory_type={self.factory_type!r}, " \
                   f"id={self.id!r})"
