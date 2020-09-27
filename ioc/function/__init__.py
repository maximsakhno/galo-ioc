from typing import (
    TypeVar,
    Any,
    Callable,
    Type,
    cast,
)
from types import (
    FunctionType,
)
from inspect import (
    Signature,
    iscoroutinefunction,
)
from ..util import (
    check_factory_type,
    generate_typed_factory_wrapper,
    get_signature,
)


__all__ = [
    "generate_function_factory",
]


F = TypeVar("F", bound=Callable)


def generate_function_factory(factory_type: Type[F], function: Callable) -> F:
    if not isinstance(function, FunctionType):
        raise ValueError(function, "Must be a function.") from None
    if iscoroutinefunction(factory_type.__call__) and not iscoroutinefunction(function):
        raise ValueError(function, "Must be a coroutine function.") from None
    factory_signature = get_factory_signature(factory_type)
    function_signature = get_signature(function)
    if function_signature != factory_signature:
        raise ValueError(factory_type, function, "Must have equal signatures.") from None
    return generate_typed_factory_wrapper(factory_type, function)


def get_factory_signature(factory_type: Type[Any]) -> Signature:
    check_factory_type(factory_type)
    signature = get_signature(cast(FunctionType, factory_type.__call__))
    return signature.replace(parameters=tuple(signature.parameters.values())[1:])
