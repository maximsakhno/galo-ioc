from typing import (
    Any,
    Optional,
    Tuple,
    List,
    Type,
    Callable,
)
from types import (
    TracebackType,
)
from uuid import (
    uuid4,
)
from contextvars import (
    Token,
    ContextVar,
)
from functools import (
    lru_cache,
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
from .nested_factory_storage import (
    NestedFactoryStorage,
)


__all__ = [
    "FactoryStorageNotFoundException",
    "FactoryStorageContextManager",
    "get_factory_storage",
    "get_factory_getter",
    "get_factory_setter",
    "get_factory",
    "set_factory",
    "use_factory",
]


class FactoryStorageNotFoundException(Exception):
    pass


factory_storage_var: ContextVar[FactoryStorage] = ContextVar(str(uuid4()))


class FactoryStorageContextManager:
    def __init__(self, storage: FactoryStorage) -> None:
        self.__storage = storage
        self.__tokens: List[Token[FactoryStorage]] = []

    def __enter__(self) -> FactoryStorage:
        try:
            storage = factory_storage_var.get()
        except LookupError:
            storage = self.__storage
        else:
            storage = NestedFactoryStorage(self.__storage, storage)
        self.__tokens.append(factory_storage_var.set(storage))
        return storage

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        factory_storage_var.reset(self.__tokens.pop())


def get_factory_storage() -> FactoryStorage:
    try:
        return factory_storage_var.get()
    except LookupError:
        raise FactoryStorageNotFoundException() from None


@lru_cache
def get_factory_getter(key: Key[F]) -> Callable[[], F]:
    def get_factory() -> F:
        factory_storage = get_factory_storage()
        return factory_storage[key]

    return get_factory


@lru_cache
def get_factory_setter(key: Key[F]) -> Callable[[F], None]:
    def set_factory(factory: F) -> None:
        factory_storage = get_factory_storage()
        factory_storage[key] = factory

    return set_factory


@lru_cache
def get_factory(key: Key[F]) -> F:
    factory_type = key.factory_type
    check_factory_type(factory_type)

    class Factory(factory_type):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            factory_storage = get_factory_storage()
            factory = factory_storage[key]
            return factory(*args, **kwargs)

    return Factory()


def set_factory(key: Key[F], factory: F) -> None:
    get_factory_storage()[key] = factory


def use_factory(key: Key[F]) -> Tuple[F, Callable[[F], None]]:
    return get_factory(key), get_factory_setter(key)
