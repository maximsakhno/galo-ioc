from typing import (
    TypeVar,
    Any,
    Callable,
    Collection,
)
from itertools import (
    chain,
)
from ..core import (
    FactoryNotFoundException,
    Key,
    FactoryStorage,
)


__all__ = [
    "NestedFactoryStorage",
]


F = TypeVar("F", bound=Callable)


class NestedFactoryStorage(FactoryStorage):
    __slots__ = (
        "__nested_factory_storage",
        "__parent_factory_storage",
    )

    def __init__(
        self,
        nested_factory_storage: FactoryStorage,
        parent_factory_storage: FactoryStorage,
    ) -> None:
        self.__nested_factory_storage = nested_factory_storage
        self.__parent_factory_storage = parent_factory_storage

    @property
    def keys(self) -> Collection[Key[Any]]:
        return frozenset(chain(self.__nested_factory_storage.keys, self.__parent_factory_storage.keys))

    def get_factory(self, key: Key[F]) -> F:
        try:
            return self.__nested_factory_storage.get_factory(key)
        except FactoryNotFoundException:
            return self.__parent_factory_storage.get_factory(key)

    def set_factory(self, key: Key[F], factory: F) -> None:
        self.__nested_factory_storage.set_factory(key, factory)
