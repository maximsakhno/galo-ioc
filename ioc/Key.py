from typing import (
    TypeVar,
    Generic,
    Optional,
    Any,
    Callable,
    Type,
    final,
)


__all__ = [
    "Key",
]


F = TypeVar("F", bound=Callable)


@final
class Key(Generic[F]):
    __slots__ = (
        "__factory_type",
        "__id",
    )

    def __init__(self, factory_type: Type[F], id: Optional[Any] = None) -> None:
        self.__factory_type = factory_type
        self.__id = id

    @property
    def factory_type(self) -> Type[F]:
        return self.__factory_type

    @property
    def id(self) -> Optional[Any]:
        return self.__id

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Key) and \
               self.__factory_type == other.__factory_type and \
               self.__id == other.__id

    def __hash__(self) -> int:
        return hash((self.__factory_type, self.__id))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" \
               f"factory_type={self.__factory_type!r}, " \
               f"id={self.__id!r})"
