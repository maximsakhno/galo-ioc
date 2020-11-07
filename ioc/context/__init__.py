from typing import (
    TypeVar,
    Optional,
    Any,
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
from ..util import (
    lru_cache,
    generate_typed_factory_wrapper,
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
    "get_factory",
    "set_factory",
    "get_factory_setter",
    "use_factory",
]


F = TypeVar("F", bound=Callable)


factory_storage_var: ContextVar[FactoryStorage] = ContextVar(str(uuid4()))


class FactoryStorageNotSetException(Exception):
    pass


class FactoryStorageContextManager:
    __slots__ = (
        "__storage",
        "__tokens",
    )

    def __init__(self, storage: FactoryStorage) -> None:
        self.__storage = storage
        self.__tokens: List[Token[Optional[FactoryStorage]]] = []

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
