from typing import TypeVar, Any, Callable, Tuple, Set, Dict


__all__ = [
    "Args",
    "KwArgs",
    "Factory",
    "FactoryType",
    "T",
    "check_factory_type",
]


Args = Tuple[Any, ...]
KwArgs = Dict[str, Any]
FactoryType = type
Factory = Callable
T = TypeVar("T")


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
        raise TypeError(f"Contains illegal attributes: "
                        f"factory_type={factory_type!r}, illegal_attribute_names={illegal_attribute_names!r}.")

    if required_attribute_names:
        raise TypeError(f"Does not contains required attributes: "
                        f"factory_type={factory_type!r}, required_attribute_names={required_attribute_names!r}.")
