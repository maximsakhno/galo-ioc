from typing import TypeVar, Protocol, Optional, Any, Callable, Type, Tuple, Set, Dict, NoReturn


__all__ = [
    "Args",
    "KwArgs",
    "Factory",
    "FactoryType",
    "T",
    "FactoryContainerException",
    "FactoryNotFoundException",
    "FactoryDecorator",
    "FactoryContainer",
    "check_factory_type",
]


Args = Tuple[Any, ...]
KwArgs = Dict[str, Any]
Factory = Callable
FactoryType = type
T = TypeVar("T")


class FactoryContainerException(Exception):
    pass


class FactoryNotFoundException(FactoryContainerException):
    pass


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


def check_factory_type(factory_type: FactoryType) -> None:
    legal_attribute_names: Set[str] = {"__module__", "__dict__", "__weakref__",
                                       "__slots__", "__doc__", "__call__"}
    illegal_attribute_names: Set[str] = set()
    required_attribute_names: Set[str] = {"__call__"}

    for base in factory_type.mro():
        if base == object:
            continue
        for name, value in vars(base).items():
            if name not in legal_attribute_names:
                illegal_attribute_names.add(name)
            required_attribute_names.discard(name)

    if illegal_attribute_names:
        raise FactoryContainerException(f"Factory type contains illegal attributes: '{factory_type}', "
                                        f"'{illegal_attribute_names}'.")

    if required_attribute_names:
        raise FactoryContainerException(f"Factory type does not contains required attributes: '{factory_type}', "
                                        f"'{required_attribute_names}'.")
