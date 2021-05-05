from typing import (
    Any,
    Iterator,
    Dict,
)
from .types import (
    F,
)
from .util import (
    check_factory_type,
)
from .interfaces import (
    Key,
    FactoryStorage,
)
from .context import (
    FactoryStorageContextManager,
)


__all__ = [
    "DictFactoryStorage",
]


class DictFactoryStorage(FactoryStorageContextManager, FactoryStorage):
    def __init__(self) -> None:
        super().__init__(self)
        self.__factories: Dict[Key, Any] = {}

    def __getitem__(self, key: Key[F]) -> F:
        return self.__factories[key]

    def __setitem__(self, key: Key[F], factory: F) -> None:
        factory_type = key.factory_type
        id = key.id

        check_factory_type(factory_type)
        if not isinstance(factory, factory_type):
            raise TypeError(f"Factory must be instance of factory type: "
                            f"'{factory}', '{factory_type}'.") from None

        for base_factory_type in factory_type.mro()[:-1]:
            base_key = Key(base_factory_type, id)
            self.__factories[base_key] = factory

    def __delitem__(self, key: Key) -> None:
        self.__factories.pop(key, None)

    def __contains__(self, key: Key) -> bool:
        return key in self.__factories

    def __len__(self) -> int:
        return len(self.__factories)

    def __iter__(self) -> Iterator[Key]:
        return iter(self.__factories)

    def __bool__(self) -> bool:
        return bool(self.__factories)
