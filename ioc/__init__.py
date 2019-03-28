from typing import Any
from typing import Callable
from typing import List
from typing import Dict
from typing import Type
from typing import get_type_hints
from types import FunctionType
from types import MethodType


__all__ = [
    "register",
    "resolve",
]


Resolver = Callable[..., Any]


def is_callable(value: Any) -> bool:
    return callable(value)


def is_type(value: Any) -> bool:
    return isinstance(value, type)


def is_method_or_function(value: Any) -> bool:
    return isinstance(value, (FunctionType, MethodType))


def is_callable_object(value: Any) -> bool:
    if is_type(value):
        return False
    if is_method_or_function(value):
        return False
    if not hasattr(value, "__call__"):
        return False
    if not is_method_or_function(getattr(value, "__call__")):
        return False
    return True


def resolve_keys(value: Any) -> List[Type[Any]]:
    try:
        if is_type(value):
            value: type
            return list(value.mro())
        if is_callable_object(value):
            value = getattr(value, "__call__")
        if is_method_or_function(value):
            return list(get_type_hints(value)["return"].mro())
        return type(value).mro()
    except Exception as e:
        raise ValueError(f"Can't get keys from '{value}'. {e}")


resolvers: Dict[Any, Resolver] = {}


def register(value: Any, *, key: Any) -> None:
    if key is not None:
        if isinstance(key, type):
            keys: List[Type[Any]] = list(key.mro())
        else:
            keys: List[Type[Any]] = [key]
    else:
        keys: List[Type[Any]] = resolve_keys(value)

    if not is_callable(value):
        for key in keys:
            resolvers[key] = lambda *args, **kwargs: value
    else:
        for key in keys:
            resolvers[key] = value


def resolve(key: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        resolver: Callable[..., Any] = resolvers[key]
    except KeyError:
        raise KeyError(f"Resolver for key '{key}' not found.")

    return resolver(*args, **kwargs)
