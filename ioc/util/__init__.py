import functools
from typing import (
    TypeVar,
    Any,
    Callable,
    Set,
    Type,
    cast,
)


__all__ = [
    "lru_cache",
    "check_factory_type",
]


C = TypeVar("C", bound=Callable)
F = TypeVar("F", bound=Callable)


def lru_cache(maxsize: int = 128, typed: bool = False) -> Callable[[C], C]:
    return cast(Callable, functools.lru_cache(maxsize, typed))


@lru_cache(1024)
def check_factory_type(factory_type: Type[Any]) -> None:
    legal_attribute_names = {"__module__", "__dict__", "__weakref__", "__slots__", "__doc__", "__call__"}
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
        raise TypeError(
            f"Factory type '{factory_type}' contains illegal "
            f"attributes '{illegal_attribute_names}'."
        ) from None

    if required_attribute_names:
        raise TypeError(
            f"Factory type '{factory_type}' does not contains "
            f"required attributes '{required_attribute_names}'."
        ) from None
