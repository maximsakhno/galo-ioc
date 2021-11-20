from typing import TypeVar, Protocol, Optional, Any, Callable, Type, Tuple, Set, Dict


__all__ = [
    "Args",
    "KwArgs",
    "Factory",
    "FactoryType",
    "T",
    "FactoryContainerException",
    "FactoryAlreadyAddedException",
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
        raise FactoryContainerException(f"Factory type contains illegal attributes: factory_type={factory_type!r}, "
                                        f"illegal_attribute_names={illegal_attribute_names!r}.")

    if required_attribute_names:
        raise FactoryContainerException(f"Factory type does not contains required attributes: "
                                        f"factory_type={factory_type!r}, "
                                        f"required_attribute_names={required_attribute_names!r}.")
