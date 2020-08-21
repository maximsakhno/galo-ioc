from typing import (
    TypeVar,
    Optional,
    Any,
    Callable,
    Tuple,
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
from ..core import (
    FactoryContainer,
)
from ..nested import (
    NestedFactoryContainer,
)


__all__ = [
    "FactoryContainerNotSetException",
    "FactoryContainerContextManager",
    "using_factory_container",
    "get_factory_container",
    "get_factory",
    "set_factory",
    "get_factory_setter",
    "use_factory",
]


E = TypeVar("E", bound=Exception)
F = TypeVar("F", bound=Callable)


factory_container_var: ContextVar[Optional[FactoryContainer]] = ContextVar(str(uuid4()), default=None)


class FactoryContainerNotSetException(Exception):
    pass


class FactoryContainerContextManager:
    __slots__ = ()

    def __enter__(self) -> None:
        raise NotImplementedError()

    def __exit__(self, exception_type: Type[E], exception: E, traceback: TracebackType) -> None:
        raise NotImplementedError()


class FactoryContainerContextManagerImpl(FactoryContainerContextManager):
    __slots__ = (
        "__factory_container",
        "__token",
    )

    def __init__(self, factory_container: FactoryContainer) -> None:
        self.__factory_container = factory_container
        self.__token: Optional[Token[Optional[FactoryContainer]]] = None

    def __enter__(self) -> None:
        if (parent_factory_container := factory_container_var.get()) is None:
            factory_container = self.__factory_container
        else:
            factory_container = NestedFactoryContainer(self.__factory_container, parent_factory_container)
        self.__token = factory_container_var.set(factory_container)

    def __exit__(self, exception_type: Type[E], exception: E, traceback: TracebackType) -> None:
        if self.__token is not None:
            factory_container_var.reset(self.__token)


def using_factory_container(factory_container: FactoryContainer) -> FactoryContainerContextManager:
    return FactoryContainerContextManagerImpl(factory_container)


def get_factory_container() -> FactoryContainer:
    if (factory_container := factory_container_var.get()) is None:
        raise FactoryContainerNotSetException()
    return factory_container


@lru_cache(1024)
def get_factory(factory_type: Type[F], id: Optional[Any] = None) -> F:
    return generate_factory_proxy(factory_type, id)


def generate_factory_proxy(factory_type: Type[F], id: Optional[Any] = None) -> F:
    def wrappee(*args: Any, **kwargs: Any) -> Any:
        return get_factory_container().get_factory(factory_type, id)(*args, **kwargs)

    return generate_typed_factory_wrapper(factory_type, wrappee)


def set_factory(factory_type: Type[F], factory: F, id: Optional[Any] = None) -> None:
    get_factory_container().set_factory(factory_type, factory, id)


@lru_cache(1024)
def get_factory_setter(factory_type: Type[F], id: Optional[Any] = None) -> Callable[[F], None]:
    return generate_factory_setter(factory_type, id)


def generate_factory_setter(factory_type: Type[F], id: Optional[Any] = None) -> Callable[[F], None]:
    def factory_setter_proxy(factory: F, /) -> None:
        set_factory(factory_type, factory, id)

    return factory_setter_proxy


def use_factory(factory_type: Type[F]) -> Tuple[F, Callable[[F], None]]:
    id = uuid4()
    return get_factory(factory_type, id), get_factory_setter(factory_type, id)
