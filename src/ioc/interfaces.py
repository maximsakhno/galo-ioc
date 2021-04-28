from typing import (
    Generic,
    Optional,
    Any,
    Iterator,
    Type,
)
from .types import (
    F,
)


__all__ = [
    "Key",
    "FactoryStorage",
]


class Key(Generic[F]):
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
        return self is other or \
               isinstance(other, Key) and \
               self.__factory_type == other.__factory_type and \
               self.__id == other.__id

    def __hash__(self) -> int:
        return hash((self.__factory_type, self.__id))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(factory_type={self.__factory_type!r}, id={self.__id!r})"


class FactoryStorage:
    def __getitem__(self, key: Key[F]) -> F:
        raise NotImplementedError()

    def __setitem__(self, key: Key[F], factory: F) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: Key) -> None:
        raise NotImplementedError()

    def __contains__(self, key: Key) -> bool:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Key]:
        raise NotImplementedError()

    def __bool__(self) -> bool:
        raise NotImplementedError()
