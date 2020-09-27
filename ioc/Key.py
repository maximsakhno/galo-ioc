from __future__ import (
    annotations,
)
from typing import (
    TypeVar,
    Generic,
    Any,
    Callable,
    Tuple,
    Dict,
    Type,
    final,
)


__all__ = [
    "Key",
]


F = TypeVar("F", bound=Callable)


class KeyMeta(type):
    __slots__ = ()

    __INSTANCES: Dict[Tuple[Type[Any], Any], Key[Any]] = {}

    def __call__(cls, factory_type: Type[Any], id: Any = "") -> Key[Any]:  # type: ignore
        instance_key = (factory_type, id)
        try:
            return cls.__INSTANCES[instance_key]
        except KeyError:
            cls.__INSTANCES[instance_key] = super().__call__(factory_type, id)
            return cls.__INSTANCES[instance_key]


@final
class Key(Generic[F], metaclass=KeyMeta):
    __slots__ = (
        "__factory_type",
        "__id",
    )

    def __init__(self, factory_type: Type[F], id: Any = "") -> None:
        self.__factory_type = factory_type
        self.__id = id

    @property
    def factory_type(self) -> Type[F]:
        return self.__factory_type

    @property
    def id(self) -> Any:
        return self.__id

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Key) and
            self.__factory_type == other.__factory_type and
            self.__id == other.__id
        )

    def __hash__(self) -> int:
        return hash((self.__factory_type, self.__id))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"factory_type={self.__factory_type!r}, "
            f"id={self.__id!r}"
            f")"
        )
