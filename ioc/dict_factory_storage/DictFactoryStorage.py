from typing import (
    TypeVar,
    Any,
    Callable,
    Iterator,
    Dict,
    final,
)
from ..util import (
    check_factory_type,
)
from ..core import (
    Key,
    FactoryStorage,
)
from ..context import (
    FactoryStorageContextManager,
)


__all__ = [
    "DictFactoryStorage",
]


F = TypeVar("F", bound=Callable)


@final
class DictFactoryStorage(FactoryStorageContextManager, FactoryStorage):
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        super().__init__(self)
        self.__factories: Dict[Key[Any], Any] = {}

    def __getitem__(self, key: Key[F]) -> F:
        return self.__factories[key]

    def __setitem__(self, key: Key[F], factory: F) -> None:
        check_factory_type(key.factory_type)
        if not isinstance(factory, key.factory_type):
            raise TypeError(factory, key.factory_type)
        self.__factories[key] = factory

    def __delitem__(self, key: Key[F]) -> None:
        self.__factories.pop(key, None)

    def __contains__(self, key: Key[Any]) -> bool:
        return key in self.__factories

    def __len__(self) -> int:
        return len(self.__factories)

    def __iter__(self) -> Iterator[Key[Any]]:
        return iter(self.__factories)

    def __bool__(self) -> bool:
        return bool(self.__factories)
