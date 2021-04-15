from typing import (
    Set,
)
from functools import (
    lru_cache,
)


__all__ = [
    "check_factory_type",
]


@lru_cache
def check_factory_type(factory_type: type) -> None:
    legal_attribute_names: Set[str] = {
        "__module__",
        "__dict__",
        "__weakref__",
        "__slots__",
        "__doc__",
        "__call__",
    }
    illegal_attribute_names: Set[str] = set()
    required_attribute_names: Set[str] = {
        "__call__",
    }

    for base in factory_type.mro():
        if base == object:
            continue
        for name, value in vars(base).items():
            if name not in legal_attribute_names:
                illegal_attribute_names.add(name)
            required_attribute_names.discard(name)

    if illegal_attribute_names:
        raise TypeError(f"Factory type '{factory_type}' contains "
                        f"illegal attributes '{illegal_attribute_names}'.") from None

    if required_attribute_names:
        raise TypeError(f"Factory type '{factory_type}' does not contains "
                        f"required attributes '{required_attribute_names}'.") from None
