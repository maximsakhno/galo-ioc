import functools
from typing import (
    TypeVar,
    Any,
    Callable,
    Iterable,
    List,
    Set,
    Dict,
    Type,
    get_type_hints,
    cast,
)
from types import (
    FunctionType,
)
from inspect import (
    Parameter,
    Signature,
    iscoroutinefunction,
)
from ..core import (
    InvalidFactoryTypeException,
)


__all__ = [
    "lru_cache",
    "check_factory_type",
    "generate_typed_factory_wrapper",
    "get_signature",
]


C = TypeVar("C", bound=Callable)
F = TypeVar("F", bound=Callable)


def lru_cache(maxsize: int = 128, typed: bool = False) -> Callable[[C], C]:
    return cast(Callable, functools.lru_cache(maxsize, typed))


@lru_cache(1024)
def check_factory_type(factory_type: Type[Any]) -> None:
    valid_attribute_names = {"__module__", "__doc__", "__slots__", "__call__"}

    invalid_attribute_names: Set[str] = set()
    missing_attribute_names: Set[str] = {"__call__"}
    for attribute_name in get_defined_attribute_names(factory_type):
        if attribute_name not in valid_attribute_names:
            invalid_attribute_names.add(attribute_name)
        missing_attribute_names.discard(attribute_name)
    if invalid_attribute_names:
        raise InvalidFactoryTypeException(factory_type, "Must not have attributes.", invalid_attribute_names) from None
    if missing_attribute_names:
        raise InvalidFactoryTypeException(factory_type, "Must have attributes.", missing_attribute_names) from None


def get_defined_attribute_names(factory_type: Type[Any]) -> Iterable[str]:
    for base_type in factory_type.mro()[:-1]:
        for attribute_name in base_type.__dict__.keys():
            yield attribute_name


SYNC_TYPED_FACTORY_WRAPPER_STMT_TEMPLATE = """
class FactoryWrapper(factory_type):
    __slots__ = ()
    def __call__{signature_stmt}:
        return wrappee({arguments_stmt})
"""


ASYNC_TYPED_FACTORY_WRAPPER_STMT_TEMPLATE = """
class FactoryWrapper(factory_type):
    __slots__ = ()
    async def __call__{signature_stmt}:
        return await wrappee({arguments_stmt})
"""


def generate_typed_factory_wrapper(factory_type: Type[F], wrappee: Callable[..., Any]) -> F:
    check_factory_type(factory_type)
    signature = get_signature(cast(FunctionType, factory_type.__call__))
    globals: Dict[str, Any] = {"factory_type": factory_type, "wrappee": wrappee}
    signature_stmt = generate_signature_stmt(globals, signature)
    arguments_stmt = generate_arguments_stmt(signature)
    if iscoroutinefunction(factory_type.__call__):
        typed_factory_wrapper_stmt_template = ASYNC_TYPED_FACTORY_WRAPPER_STMT_TEMPLATE
    else:
        typed_factory_wrapper_stmt_template = SYNC_TYPED_FACTORY_WRAPPER_STMT_TEMPLATE
    typed_factory_wrapper_stmt = typed_factory_wrapper_stmt_template.format(
        signature_stmt=signature_stmt,
        arguments_stmt=arguments_stmt,
    )
    exec(typed_factory_wrapper_stmt, globals)
    typed_factory_wrapper_type = cast(type, globals["FactoryWrapper"])
    type_hints = get_type_hints(factory_type.__call__)
    typed_factory_wrapper_type.__call__.__annotations__ = type_hints
    typed_factory_wrapper = typed_factory_wrapper_type()
    return typed_factory_wrapper


def generate_signature_stmt(globals: Dict[str, Any], signature: Signature) -> str:
    signature_stmt = f"({generate_parameters_stmt(globals, signature)})"
    if signature.return_annotation is not Parameter.empty:
        globals["return_annotation"] = signature.return_annotation
        signature_stmt = f"{signature_stmt} -> return_annotation"
    return signature_stmt


def generate_parameters_stmt(globals: Dict[str, Any], signature: Signature) -> str:
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
        else:  # parameter.kind == Parameter.VAR_KEYWORD:
            parameter_stmt = f"**{parameter.name}"

        if parameter.annotation is not Parameter.empty:
            annotation_name = f"{parameter.name}_annotation"
            globals[annotation_name] = parameter.annotation
            parameter_stmt = f"{parameter_stmt}: {annotation_name}"

        if parameter.default is not Parameter.empty:
            default_name = f"{parameter.name}_default"
            globals[default_name] = parameter.default
            parameter_stmt = f"{parameter_stmt} = {default_name}"

        parameter_stmts.append(parameter_stmt)

    if append_positional_only_delimiter:
        parameter_stmts.append("/")

    return ", ".join(parameter_stmts)


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
        else:  # parameter.kind == Parameter.VAR_KEYWORD:
            argument_stmts.append(f"**{parameter.name}")
    return ", ".join(argument_stmts)


@lru_cache(1024)
def get_signature(function: FunctionType) -> Signature:
    signature = Signature.from_callable(function)
    type_hints = get_type_hints(function)
    parameters: List[Parameter] = []
    for parameter in signature.parameters.values():
        annotation = type_hints.get(parameter.name, Parameter.empty)
        parameter = parameter.replace(annotation=annotation)
        parameters.append(parameter)
    return_annotation = type_hints.get("return", Parameter.empty)
    return signature.replace(parameters=parameters, return_annotation=return_annotation)
