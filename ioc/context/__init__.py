from typing import (
    Generic,
    TypeVar,
    Any,
    Optional,
    Callable,
    Tuple,
    List,
    Type,
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
from ..util import (
    check_factory_type,
)
from ..nested import (
    NestedFactoryStorage,
)
from ..Key import Key
from ..FactoryStorage import FactoryStorage


__all__ = [
    "FactoryStorageNotSetException",
    "FactoryStorageContextManager",
    "get_factory_storage",
    "GetFactoryFunction",
    "get_factory_getter",
    "SetFactoryFunction",
    "get_factory_setter",
    "get_factory",
    "set_factory",
    "use_factory",
]


F = TypeVar("F", bound=Callable)


class FactoryStorageNotSetException(Exception):
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
        raise FactoryStorageNotSetException() from None


class GetFactoryFunction(Generic[F]):
    def __call__(self) -> F:
        raise NotImplementedError()


@lru_cache
def get_factory_getter(key: Key[F]) -> GetFactoryFunction[F]:
    class GetFactoryFunctionImpl(GetFactoryFunction[F]):
        def __call__(self) -> F:
            factory_storage = get_factory_storage()
            return factory_storage[key]

    return GetFactoryFunctionImpl()


class SetFactoryFunction(Generic[F]):
    def __call__(self, factory: F) -> None:
        raise NotImplementedError()


@lru_cache
def get_factory_setter(key: Key[F]) -> SetFactoryFunction[F]:
    class SetFactoryFunctionImpl(SetFactoryFunction[F]):
        def __call__(self, factory: F) -> None:
            factory_storage = get_factory_storage()
            factory_storage[key] = factory

    return SetFactoryFunctionImpl()


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


def use_factory(key: Key[F]) -> Tuple[F, SetFactoryFunction[F]]:
    return get_factory(key), get_factory_setter(key)
