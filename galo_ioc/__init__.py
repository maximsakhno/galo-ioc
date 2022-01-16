"""
Provides an implementation of the service locator pattern.
"""

from contextvars import ContextVar, Token
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
)

__all__ = [
    "Args",
    "KwArgs",
    "Factory",
    "FactoryType",
    "T",
    "check_factory_type",
    "FactoryAlreadyAddedException",
    "FactoryNotFoundException",
    "FactoryDecorator",
    "FactoryContainer",
    "NoFactoryContainerInContextException",
    "FactoryContainerContextManager",
    "add_factory",
    "add_factory_decorator",
    "get_factory",
    "FactoryContainerImpl",
]


__version__ = "0.15.0"


Args = tuple
KwArgs = Dict[str, Any]
FactoryType = type
Factory = Callable
T = TypeVar("T")


def check_factory_type(factory_type: FactoryType) -> None:
    legal_attribute_names: Set[str] = {
        "__module__",
        "__dict__",
        "__weakref__",
        "__slots__",
        "__doc__",
        "__call__",
    }
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
        raise Exception(
            f"Contains illegal attributes: "
            f"factory_type={factory_type!r}, "
            f"illegal_attribute_names={illegal_attribute_names!r}."
        )

    if required_attribute_names:
        raise Exception(
            f"Does not contains required attributes: "
            f"factory_type={factory_type!r}, "
            f"required_attribute_names={required_attribute_names!r}."
        )


class FactoryAlreadyAddedException(Exception):
    def __init__(self, factory_type: FactoryType, id: Optional[str]) -> None:
        super().__init__(f"Factory already added: factory_type={factory_type!r}, id={id!r}.")


class FactoryNotFoundException(Exception):
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

    def call_factory(
        self,
        factory_type: FactoryType,
        id: Optional[str],
        args: Args,
        kwargs: KwArgs,
    ) -> Any:
        raise NotImplementedError()


factory_containers_var: ContextVar[Tuple[FactoryContainer, ...]] = ContextVar(
    "factory_containers", default=()
)


class NoFactoryContainerInContextException(Exception):
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
    class Factory(factory_type):  # type: ignore
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return call_factory(factory_type, id, args, kwargs)

    return Factory()


class FactoryKey(NamedTuple):
    factory_type: FactoryType
    id: Optional[str]


class FactoryContainerImpl(FactoryContainerContextManager):
    def __init__(self) -> None:
        super().__init__()
        self.__factories: Dict[FactoryKey, Factory] = {}
        self.__factory_decorators: List[FactoryDecorator] = []

    def add_factory(self, factory_type: Type[T], factory: T, id: Optional[str] = None) -> None:
        factory_key = FactoryKey(factory_type, id)
        if factory_key in self.__factories:
            raise FactoryAlreadyAddedException(factory_type, id)
        check_factory_type(factory_type)
        for factory_decorator in self.__factory_decorators:
            factory = factory_decorator(factory_type, id, factory)  # type: ignore
        self.__factories[factory_key] = factory  # type: ignore

    def add_factory_decorator(self, factory_decorator: FactoryDecorator) -> None:
        for factory_key in self.__factories.keys():
            factory_type, id = factory_key
            factory = self.__factories[factory_key]
            self.__factories[factory_key] = factory_decorator(factory_type, id, factory)
        self.__factory_decorators.append(factory_decorator)

    def call_factory(
        self,
        factory_type: FactoryType,
        id: Optional[str],
        args: Args,
        kwargs: KwArgs,
    ) -> Any:
        factory_key = FactoryKey(factory_type, id)
        try:
            factory = self.__factories[factory_key]
        except KeyError:
            raise FactoryNotFoundException(factory_type, id) from None
        return factory(*args, **kwargs)
