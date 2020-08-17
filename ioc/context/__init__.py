from typing import (
    TypeVar,
    Union,
    Optional,
    Any,
    Callable,
    Iterable,
    Tuple,
    List,
    Dict,
    Type,
    cast,
    get_type_hints,
)
from types import (
    FunctionType,
    TracebackType,
)
from uuid import (
    uuid4,
)
from contextvars import (
    Token,
    ContextVar,
)
from inspect import (
    Parameter,
    Signature,
    iscoroutinefunction,
)
from functools import (
    lru_cache,
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
    "get_instance",
]


E = TypeVar("E", bound=Exception)
F = TypeVar("F")
I = TypeVar("I")


factory_container_var: ContextVar[Optional[FactoryContainer]] = ContextVar(str(uuid4()), default=None)


class FactoryContainerNotSetException(Exception):
    pass


class InvalidInstanceTypeException(Exception):
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
        self.__token: Optional[Token[FactoryContainer]] = None

    def __enter__(self) -> None:
        if (parent_factory_container := factory_container_var.get()) is None:
            factory_container = self.__factory_container
        else:
            factory_container = NestedFactoryContainer(self.__factory_container, parent_factory_container)
        self.__token = factory_container_var.set(factory_container)

    def __exit__(self, exception_type: Type[E], exception: E, traceback: TracebackType) -> None:
        factory_container_var.reset(self.__token)


def using_factory_container(factory_container: FactoryContainer) -> FactoryContainerContextManager:
    return FactoryContainerContextManagerImpl(factory_container)


def get_factory_container() -> FactoryContainer:
    if (factory_container := factory_container_var.get()) is None:
        raise FactoryContainerNotSetException()
    return factory_container


@lru_cache(1024)
def get_factory(factory_type: Type[F], id: Optional[Any] = None) -> F:

    def factory_proxy(*args: Any, **kwargs: Any) -> Any:
        return get_factory_container().get_factory(factory_type, id)(*args, **kwargs)

    return factory_proxy


def set_factory(factory_type: Type[F], factory: F, id: Optional[Any] = None) -> None:
    get_factory_container().set_factory(factory_type, factory, id)


@lru_cache(1024)
def get_factory_setter(factory_type: Type[F], id: Optional[Any] = None) -> Callable[[F], None]:

    def factory_setter_proxy(factory: F, /) -> None:
        set_factory(factory_type, factory, id)

    return factory_setter_proxy


def use_factory(factory_type: Type[F]) -> Tuple[F, Callable[[F], None]]:
    id = uuid4()
    return get_factory(factory_type, id), get_factory_setter(factory_type, id)


def get_instance(instance_type: Type[I], factory: Callable[[], I]) -> I:
    check_instance_type(instance_type)
    return generate_instance_proxy(instance_type, factory)


@lru_cache(1024)
def check_instance_type(instance_type: Type[Any]) -> None:
    ignored_names = {"__module__", "__doc__", "__slots__"}
    valid_names = {"__call__"}
    invalid_names = {"__init__"}

    for name, member in get_members(instance_type):
        if name in ignored_names:
            continue

        if not isinstance(member, (property, staticmethod, classmethod, FunctionType)):
            message = f"Type must be {Union[property, staticmethod, classmethod, FunctionType]}."
            raise InvalidInstanceTypeException(instance_type, name, message) from None

        if isinstance(member, (staticmethod, classmethod)) and not isinstance(member.__func__, FunctionType):
            message = f"{classmethod} or {staticmethod} must wrap a {FunctionType}."
            raise InvalidInstanceTypeException(instance_type, name, message) from None

        if name in invalid_names:
            message = f"Attribute is invalid."
            raise InvalidInstanceTypeException(instance_type, name, message) from None

        if name.startswith("_") and name not in valid_names:
            message = f"Private attributes are invalid."
            raise InvalidInstanceTypeException(instance_type, name, message) from None


def generate_instance_proxy(instance_type: Type[I], factory: Callable[[], I]) -> I:
    namespace: Dict[str, Any] = {"__slots__": ()}

    for name, _ in get_properties(instance_type):
        property_proxy = generate_property_proxy(name, factory)
        namespace[name] = property_proxy

    for name, static_method in get_static_methods(instance_type):
        function = cast(FunctionType, static_method.__func__)
        function_proxy = generate_function_proxy(function, factory)
        namespace[name] = staticmethod(function_proxy)

    for name, class_method in get_class_methods(instance_type):
        function = cast(FunctionType, class_method.__func__)
        function_proxy = generate_function_proxy(function, factory)
        namespace[name] = classmethod(function_proxy)

    for name, function in get_functions(instance_type):
        function_proxy = generate_function_proxy(function, factory)
        namespace[name] = function_proxy

    instance_proxy_type = type(f"{instance_type.__name__}Proxy", (instance_type,), namespace)
    return instance_proxy_type()


def get_properties(type: Type[Any]) -> Iterable[Tuple[str, property]]:
    return ((name, member) for name, member in get_members(type) if isinstance(member, property))


def get_static_methods(type: Type[Any]) -> Iterable[Tuple[str, staticmethod]]:
    return ((name, member) for name, member in get_members(type) if isinstance(member, staticmethod))


def get_class_methods(type: Type[Any]) -> Iterable[Tuple[str, classmethod]]:
    return ((name, member) for name, member in get_members(type) if isinstance(member, classmethod))


def get_functions(type: Type[Any]) -> Iterable[Tuple[str, FunctionType]]:
    return ((name, member) for name, member in get_members(type) if isinstance(member, FunctionType))


def get_members(type: Type[Any]) -> Iterable[Tuple[str, Any]]:
    for base_type in type.mro()[:-1]:
        for name, member in base_type.__dict__.items():
            yield name, member


def generate_property_proxy(name: str, factory: Callable[[], Any]) -> property:
    return property(
        fget=lambda self: getattr(factory(), name),
        fset=lambda self, value: setattr(factory(), name, value),
        fdel=lambda self: delattr(factory(), name),
    )


def generate_function_proxy(function: FunctionType, factory: Callable[[], Any]) -> FunctionType:
    signature = Signature.from_callable(function)
    type_hints = get_type_hints(function)
    globals: Dict[str, Any] = {"factory": factory}
    body_stmt = f"\treturn factory().{function.__name__}({generate_arguments_stmt(signature)})"
    function_def_stmt = f"def {function.__name__}{generate_signature_stmt(globals, signature, type_hints)}{body_stmt}"
    if iscoroutinefunction(function):
        function_def_stmt = f"async {function_def_stmt}"
    exec(function_def_stmt, globals)
    return globals[function.__name__]


def generate_arguments_stmt(signature: Signature) -> str:
    argument_stmts: List[str] = []
    for parameter in signature.parameters.values():
        if parameter.name in ("cls", "self"):
            continue
        if parameter.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            argument_stmts.append(parameter.name)
        elif parameter.kind == Parameter.KEYWORD_ONLY:
            argument_stmts.append(f"{parameter.name}={parameter.name}")
        elif parameter.kind == Parameter.VAR_POSITIONAL:
            argument_stmts.append(f"*{parameter.name}")
        elif parameter.kind == Parameter.VAR_KEYWORD:
            argument_stmts.append(f"**{parameter.name}")
        else:
            raise TypeError(f"Illegal parameter kind '{parameter.kind}'.")
    return ", ".join(argument_stmts)


def generate_signature_stmt(globals: Dict[str, Any], signature: Signature, type_hints: Dict[str, Any]) -> str:
    signature_stmt = f"({generate_parameters_stmt(globals, signature, type_hints)})"
    if signature.return_annotation is Parameter.empty:
        signature_stmt = f"{signature_stmt}:"
    else:
        globals["return_annotation"] = type_hints["return"]
        signature_stmt = f"{signature_stmt} -> return_annotation:"
    return signature_stmt


def generate_parameters_stmt(globals: Dict[str, Any], signature: Signature, type_hints: Dict[str, Any]) -> str:
    append_positional_only_delimiter = False
    append_keyword_only_delimiter = True

    parameter_stmts: List[str] = []
    for parameter in signature.parameters.values():
        if parameter.kind is Parameter.POSITIONAL_ONLY:
            append_positional_only_delimiter = True
        elif append_positional_only_delimiter:
            parameter_stmts.append("/")
            append_positional_only_delimiter = False

        if parameter.kind is Parameter.KEYWORD_ONLY and append_keyword_only_delimiter:
            parameter_stmts.append("*")
            append_keyword_only_delimiter = False

        if parameter.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
            parameter_stmt = parameter.name
        elif parameter.kind == Parameter.VAR_POSITIONAL:
            parameter_stmt = f"*{parameter.name}"
        elif parameter.kind == Parameter.VAR_KEYWORD:
            parameter_stmt = f"**{parameter.name}"
        else:
            raise TypeError(f"Illegal parameter kind '{parameter.kind}'.")

        if parameter.annotation is not Parameter.empty:
            annotation_name = f"{parameter.name}_annotation"
            globals[annotation_name] = type_hints[parameter.name]
            parameter_stmt = f"{parameter_stmt}: {annotation_name}"

        if parameter.default is not Parameter.empty:
            default_name = f"{parameter.name}_default"
            globals[default_name] = parameter.default
            parameter_stmt = f"{parameter_stmt} = {default_name}"

        parameter_stmts.append(parameter_stmt)

    if append_positional_only_delimiter:
        parameter_stmts.append("/")

    return ", ".join(parameter_stmts)
