from typing import Optional, Any, Iterator, List, Type
from contextlib import contextmanager
from contextvars import ContextVar
from . import (Args, KwArgs, FactoryType, T, FactoryContainerException, FactoryNotFoundException, FactoryDecorator,
               FactoryContainer)
from .factory_container_impl import FactoryContainerImpl


__all__ = [
    "factory_container",
    "add_factory",
    "add_factory_decorator",
    "get_factory",
]


factory_containers_var: ContextVar[List[FactoryContainer]] = ContextVar("factory_containers")


def get_factory_containers() -> List[FactoryContainer]:
    try:
        return factory_containers_var.get()
    except LookupError:
        factory_containers = []
        factory_containers_var.set(factory_containers)
        return factory_containers


def get_not_empty_factory_containers() -> List[FactoryContainer]:
    factory_containers = get_factory_containers()
    if not factory_containers:
        raise FactoryContainerException(f"No factory containers.")
    return factory_containers


@contextmanager
def factory_container(factory_container: Optional[FactoryContainer] = None) -> Iterator[None]:
    if factory_container is None:
        factory_container = FactoryContainerImpl()

    factory_containers = get_factory_containers()
    factory_containers.append(factory_container)
    try:
        yield
    finally:
        factory_containers.pop()


def add_factory(factory_type: Type[T], factory: T, id: Optional[str] = None) -> None:
    factory_containers = get_not_empty_factory_containers()
    factory_containers[-1].add_factory(factory_type, factory, id)


def add_factory_decorator(factory_decorator: FactoryDecorator) -> None:
    factory_containers = get_not_empty_factory_containers()
    factory_containers[-1].add_factory_decorator(factory_decorator)


def call_factory(factory_type: FactoryType, id: Optional[str], args: Args, kwargs: KwArgs) -> Any:
    factory_containers = get_not_empty_factory_containers()
    for factory_container in reversed(factory_containers):
        try:
            return factory_container.call_factory(factory_type, id, args, kwargs)
        except FactoryNotFoundException:
            continue
    raise FactoryNotFoundException(f"Factory not found: factory_type={factory_type!r}, id={id!r}.")


def get_factory(factory_type: Type[T], id: Optional[str] = None) -> T:
    class Factory(factory_type):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return call_factory(factory_type, id, args, kwargs)

    return Factory()
