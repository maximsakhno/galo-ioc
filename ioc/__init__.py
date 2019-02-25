from typing import Any
from typing import Callable
from typing import Dict


__all__ = [
    "register",
    "resolve",
    "Singleton",
]


resolvers: Dict[Any, Callable[..., Any]] = {}


def register(key: Any, value: Any) -> None:
    if callable(value):
        resolvers[key] = value
    else:
        resolvers[key] = lambda: value


def resolve(key: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        resolver: Callable[..., Any] = resolvers[key]
    except KeyError:
        raise KeyError(f"Resolver for key '{key}' not found.")

    return resolver(*args, **kwargs)


class Singleton:
    __slots__ = (
        "__instance",
    )

    def __init__(self, instance: Any) -> None:
        self.__instance: Any = instance

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.__instance
