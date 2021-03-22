from typing import (
    TypeVar,
    Any,
    Callable,
    Iterator,
)
from itertools import (
    chain,
)
from ..Key import Key
from ..FactoryStorage import FactoryStorage


__all__ = [
    "NestedFactoryStorage",
]


F = TypeVar("F", bound=Callable)


class NestedFactoryStorage(FactoryStorage):
    def __init__(self, nested: FactoryStorage, parent: FactoryStorage) -> None:
        self.__nested = nested
        self.__parent = parent

    def __getitem__(self, key: Key[F]) -> F:
        try:
            return self.__nested[key]
        except KeyError:
            return self.__parent[key]

    def __setitem__(self, key: Key[F], factory: F) -> None:
        self.__nested[key] = factory

    def __delitem__(self, key: Key[Any]) -> None:
        del self.__nested[key]

    def __contains__(self, key: Key[Any]) -> bool:
        return key in self.__nested or key in self.__parent

    def __len__(self) -> int:
        return len(set(chain(self.__nested, self.__parent)))

    def __iter__(self) -> Iterator[Key[Any]]:
        return iter(set(chain(self.__nested, self.__parent)))

    def __bool__(self) -> bool:
        return bool(self.__nested) or bool(self.__parent)
