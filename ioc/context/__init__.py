from typing import (
    TypeVar,
    Optional,
    Any,
    Callable,
    ContextManager,
    Tuple,
    Type,
    Literal,
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
from ..util import (
    lru_cache,
    generate_typed_factory_wrapper,
)
from ..core import (
    Key,
    FactoryStorage,
)
from ..nested_factory_storage import (
    NestedFactoryStorage,
)


__all__ = [
    "FactoryStorageSetException",
    "FactoryStorageNotSetException",
    "FactoryStorageContextManager",
    "get_factory_storage",
    "get_factory",
    "set_factory",
    "get_factory_setter",
    "use_factory",
]


F = TypeVar("F", bound=Callable)


factory_storage_var: ContextVar[FactoryStorage] = ContextVar(str(uuid4()))


class FactoryStorageNotSetException(Exception):
    pass


class FactoryStorageSetException(Exception):
    pass


class FactoryStorageContextManager(ContextManager[FactoryStorage]):
    __slots__ = (
        "__storage",
        "__token",
    )

    def __init__(self, storage: FactoryStorage) -> None:
        self.__storage = storage
        self.__token: Optional[Token[FactoryStorage]] = None

    def __enter__(self) -> FactoryStorage:
        if self.__token is not None:
            raise FactoryStorageSetException() from None
        try:
            storage = factory_storage_var.get()
        except LookupError:
            storage = self.__storage
        else:
            storage = NestedFactoryStorage(self.__storage, storage)
        self.__token = factory_storage_var.set(storage)
        return storage

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Literal[False]:
        if self.__token is not None:
            factory_storage_var.reset(self.__token)
        return False


def get_factory_storage() -> FactoryStorage:
    try:
        return factory_storage_var.get()
    except LookupError:
        raise FactoryStorageNotSetException() from None


@lru_cache(1024)
def get_factory(key: Key[F]) -> F:
    return generate_factory_proxy(key)


def generate_factory_proxy(key: Key[F]) -> F:
    def wrappee(*args: Any, **kwargs: Any) -> Any:
        return get_factory_storage()[key](*args, **kwargs)

    return generate_typed_factory_wrapper(key.factory_type, wrappee)


def set_factory(key: Key[F], factory: F) -> None:
    get_factory_storage()[key] = factory


@lru_cache(1024)
def get_factory_setter(key: Key[F]) -> Callable[[F], None]:
    return generate_factory_setter(key)


def generate_factory_setter(key: Key[F]) -> Callable[[F], None]:
    def factory_setter_proxy(factory: F) -> None:
        set_factory(key, factory)

    return factory_setter_proxy


def use_factory(key: Key[F]) -> Tuple[F, Callable[[F], None]]:
    return get_factory(key), get_factory_setter(key)
