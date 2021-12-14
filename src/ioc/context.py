from types import TracebackType
from typing import Optional, Any, Tuple, Type
from contextvars import ContextVar, Token
from ioc import Args, KwArgs, FactoryType, T
from ioc.factory_containers import (FactoryContainerException, FactoryNotFoundException, FactoryDecorator,
                                    FactoryContainer)


__all__ = [
    "NoFactoryContainerInContextException",
    "FactoryContainerContextManager",
    "add_factory",
    "add_factory_decorator",
    "get_factory",
]


factory_containers_var: ContextVar[Tuple[FactoryContainer, ...]] = ContextVar("factory_containers", default=())


class NoFactoryContainerInContextException(FactoryContainerException):
    def __init__(self) -> None:
        super().__init__("No factory container in context.")


class FactoryContainerContextManager(FactoryContainer):
    def __init__(self) -> None:
        self.__token: Optional[Token[Tuple[FactoryContainer, ...]]] = None

    def __enter__(self) -> None:
        self.__token = factory_containers_var.set((*factory_containers_var.get(), self))

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.__token is not None:
            factory_containers_var.reset(self.__token)


def get_last_factory_container() -> FactoryContainer:
    factory_containers = factory_containers_var.get()
    try:
        return factory_containers[-1]
    except IndexError:
        raise NoFactoryContainerInContextException() from None


def add_factory(factory_type: Type[T], factory: T, id: Optional[str] = None) -> None:
    get_last_factory_container().add_factory(factory_type, factory, id)


def add_factory_decorator(factory_decorator: FactoryDecorator) -> None:
    get_last_factory_container().add_factory_decorator(factory_decorator)


def call_factory(factory_type: FactoryType, id: Optional[str], args: Args, kwargs: KwArgs) -> Any:
    factory_containers = factory_containers_var.get()
    if not factory_containers:
        raise NoFactoryContainerInContextException() from None

    for factory_container in reversed(factory_containers):
        try:
            return factory_container.call_factory(factory_type, id, args, kwargs)
        except FactoryNotFoundException:
            continue
    raise FactoryNotFoundException(factory_type, id) from None


def get_factory(factory_type: Type[T], id: Optional[str] = None) -> T:
    class Factory(factory_type):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return call_factory(factory_type, id, args, kwargs)

    return Factory()
