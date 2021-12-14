from typing import Protocol, Optional, Any, Type
from ioc import Args, KwArgs, FactoryType, Factory, T


__all__ = [
    "FactoryContainerException",
    "FactoryAlreadyAddedException",
    "FactoryNotFoundException",
    "FactoryDecorator",
    "FactoryContainer",
]


class FactoryContainerException(Exception):
    pass


class FactoryAlreadyAddedException(FactoryContainerException):
    def __init__(self, factory_type: FactoryType, id: Optional[str]) -> None:
        super().__init__(f"Factory already added: factory_type={factory_type!r}, id={id!r}.")


class FactoryNotFoundException(FactoryContainerException):
    def __init__(self, factory_type: FactoryType, id: Optional[str]) -> None:
        super().__init__(f"Factory not found: factory_type={factory_type!r}, id={id!r}.")


class FactoryDecorator(Protocol):
    def __call__(self, factory_type: FactoryType, id: Optional[str], factory: Factory) -> Factory:
        raise NotImplementedError()


class FactoryContainer:
    def add_factory(self, factory_type: Type[T], factory: T, id: Optional[str] = None) -> None:
        raise NotImplementedError()

    def add_factory_decorator(self, factory_decorator: FactoryDecorator) -> None:
        raise NotImplementedError()

    def call_factory(self, factory_type: FactoryType, id: Optional[str], args: Args, kwargs: KwArgs) -> Any:
        raise NotImplementedError()
