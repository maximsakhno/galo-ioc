from typing import (
    TypeVar,
    Any,
    Callable,
    Collection,
    Dict,
)
from ..util import (
    check_factory_type,
)
from ..core import (
    InvalidFactoryException,
    FactoryNotFoundException,
    Key,
    FactoryStorage,
)


__all__ = [
    "DictFactoryStorage",
]


F = TypeVar("F", bound=Callable)


class DictFactoryStorage(FactoryStorage):
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[Key[Any], Any] = {}

    @property
    def keys(self) -> Collection[Key[Callable]]:
        return frozenset(self.__factories.keys())

    def get_factory(self, key: Key[F]) -> F:
        check_factory_type(key.factory_type)
        try:
            return self.__factories[key]
        except KeyError:
            raise FactoryNotFoundException(key) from None

    def set_factory(self, key: Key[F], factory: F) -> None:
        check_factory_type(key.factory_type)
        if not isinstance(factory, key.factory_type):
            raise InvalidFactoryException(factory, f"Must be instance of '{key.factory_type}'") from None
        self.__factories[key] = factory
