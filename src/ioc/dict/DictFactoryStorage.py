from typing import (
    TypeVar,
    Any,
    Callable,
    Iterator,
    Dict,
)
from ..util import (
    check_factory_type,
)
from ..context import (
    FactoryStorageContextManager,
)
from ..Key import Key
from ..FactoryStorage import FactoryStorage


__all__ = [
    "DictFactoryStorage",
]


F = TypeVar("F", bound=Callable)


class DictFactoryStorage(FactoryStorageContextManager, FactoryStorage):
    def __init__(self) -> None:
        super().__init__(self)
        self.__factories: Dict[Key[Any], Any] = {}

    def __getitem__(self, key: Key[F]) -> F:
        return self.__factories[key]

    def __setitem__(self, key: Key[F], factory: F) -> None:
        factory_type = key.factory_type
        check_factory_type(factory_type)
        if not isinstance(factory, factory_type):
            raise TypeError(f"Factory '{factory}' must be instance of '{factory_type}'.") from None
        self.__factories[key] = factory

    def __delitem__(self, key: Key[Any]) -> None:
        self.__factories.pop(key, None)

    def __contains__(self, key: Key[Any]) -> bool:
        return key in self.__factories

    def __len__(self) -> int:
        return len(self.__factories)

    def __iter__(self) -> Iterator[Key[Any]]:
        return iter(self.__factories)

    def __bool__(self) -> bool:
        return bool(self.__factories)
