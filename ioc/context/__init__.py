from typing import (
    Generic,
    TypeVar,
    Any,
    Optional,
    Callable,
    Tuple,
    List,
    Type,
    cast,
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
from asyncio import (
    iscoroutinefunction,
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
    "GetsFactory",
    "SetsFactory",
    "get_factory_storage",
    "get_factory_getter",
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


class GetsFactory(Generic[F]):
    @property
    def key(self) -> Key[F]:
        raise NotImplementedError()


class SetsFactory(Generic[F]):
    @property
    def key(self) -> Key[F]:
        raise NotImplementedError()


def get_factory_storage() -> FactoryStorage:
    try:
        return factory_storage_var.get()
    except LookupError:
        raise FactoryStorageNotSetException() from None


@lru_cache
def get_factory_getter(key: Key[F]) -> Callable[[], F]:
    class FactoryGetter(GetsFactory[F]):
        @property
        def key(self) -> Key[F]:
            return key

        def __call__(self) -> F:
            return get_factory_storage()[key]

    return FactoryGetter()


@lru_cache
def get_factory_setter(key: Key[F]) -> Callable[[F], None]:
    class FactorySetter(SetsFactory[F]):
        @property
        def key(self) -> Key[F]:
            return key

        def __call__(self, factory: F) -> None:
            get_factory_storage()[key] = factory

    return FactorySetter()


@lru_cache
def get_factory(key: Key[F]) -> F:
    factory_type = key.factory_type
    check_factory_type(factory_type)

    class Factory(factory_type, GetsFactory[F]):
        @property
        def key(self) -> Key[F]:
            return key

        if iscoroutinefunction(factory_type.__call__):
            async def __call__(self, *args: Any, **kwargs: Any) -> Any:
                return await get_factory_storage()[key](*args, **kwargs)
        else:
            def __call__(self, *args: Any, **kwargs: Any) -> Any:
                return get_factory_storage()[key](*args, **kwargs)

    return cast(F, Factory())


def set_factory(key: Key[F], factory: F) -> None:
    get_factory_storage()[key] = factory


def use_factory(key: Key[F]) -> Tuple[F, Callable[[F], None]]:
    return get_factory(key), get_factory_setter(key)
