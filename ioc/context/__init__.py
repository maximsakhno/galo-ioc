from typing import (
    TypeVar,
    Optional,
    Any,
    Callable,
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
    "FactoryStorageNotSetException",
    "FactoryStorageContextManager",
    "using_factory_storage",
    "get_factory_storage",
    "get_factory",
    "set_factory",
    "get_factory_setter",
    "use_factory",
]


F = TypeVar("F", bound=Callable)


factory_storage_var: ContextVar[Optional[FactoryStorage]] = ContextVar(str(uuid4()), default=None)


class FactoryStorageNotSetException(Exception):
    pass


class FactoryStorageContextManager:
    __slots__ = ()

    def __enter__(self) -> FactoryStorage:
        raise NotImplementedError()

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: TracebackType,
    ) -> Optional[bool]:
        raise NotImplementedError()


class FactoryStorageContextManagerImpl(FactoryStorageContextManager):
    __slots__ = (
        "__factory_storage",
        "__token",
    )

    def __init__(self, factory_storage: FactoryStorage) -> None:
        self.__factory_storage = factory_storage
        self.__token: Optional[Token[Optional[FactoryStorage]]] = None

    def __enter__(self) -> FactoryStorage:
        if (parent_factory_storage := factory_storage_var.get()) is None:
            factory_storage = self.__factory_storage
        else:
            factory_storage = NestedFactoryStorage(
                nested_factory_storage=self.__factory_storage,
                parent_factory_storage=parent_factory_storage,
            )
        self.__token = factory_storage_var.set(factory_storage)
        return factory_storage

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: TracebackType,
    ) -> Literal[False]:
        if self.__token is not None:
            factory_storage_var.reset(self.__token)
        return False


def using_factory_storage(factory_storage: FactoryStorage) -> FactoryStorageContextManager:
    return FactoryStorageContextManagerImpl(factory_storage)


def get_factory_storage() -> FactoryStorage:
    if (factory_storage := factory_storage_var.get()) is None:
        raise FactoryStorageNotSetException()
    return factory_storage


@lru_cache(1024)
def get_factory(key: Key[F]) -> F:
    return generate_factory_proxy(key)


def generate_factory_proxy(key: Key[F]) -> F:
    def wrappee(*args: Any, **kwargs: Any) -> Any:
        return get_factory_storage().get_factory(key)(*args, **kwargs)

    return generate_typed_factory_wrapper(key.factory_type, wrappee)


def set_factory(key: Key[F], factory: F) -> None:
    get_factory_storage().set_factory(key, factory)


@lru_cache(1024)
def get_factory_setter(key: Key[F]) -> Callable[[F], None]:
    return generate_factory_setter(key)


def generate_factory_setter(key: Key[F]) -> Callable[[F], None]:
    def factory_setter_proxy(factory: F) -> None:
        set_factory(key, factory)

    return factory_setter_proxy


def use_factory(key: Key[F]) -> Tuple[F, Callable[[F], None]]:
    return get_factory(key), get_factory_setter(key)
