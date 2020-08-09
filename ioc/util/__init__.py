from typing import (
    Protocol,
    Any,
    Callable,
    List,
    Type,
    get_type_hints,
)
from inspect import (
    Parameter,
    Signature,
)
from functools import (
    lru_cache,
)


__all__ = [
    "InvalidFactoryTypeException",
    "check_factory_type",
    "get_signature",
]


class InvalidFactoryTypeException(Exception):
    pass


@lru_cache(1024)
def check_factory_type(factory_type: Type[Any]) -> None:
    if Protocol not in factory_type.mro():
        raise InvalidFactoryTypeException(factory_type, f"Must be a protocol.") from None

    public_attribute_names: List[str] = []

    for attribute_name in dir(factory_type):
        if not attribute_name.startswith("_"):
            public_attribute_names.append(attribute_name)

    if public_attribute_names:
        raise InvalidFactoryTypeException(factory_type, "Public attributes are not allowed.", public_attribute_names) from None

    if not issubclass(factory_type, Callable):
        raise InvalidFactoryTypeException(factory_type, "Must be a callable.") from None


@lru_cache(1024)
def get_signature(factory_type: Type[Any]) -> Signature:
    check_factory_type(factory_type)
    signature = Signature.from_callable(factory_type.__call__)
    type_hints = get_type_hints(factory_type.__call__)
    parameters: List[Parameter] = []
    for parameter in signature.parameters.values():
        annotation = type_hints.get(parameter.name, Parameter.empty)
        parameter = parameter.replace(annotation=annotation)
        parameters.append(parameter)
    return_annotation = type_hints.get("return", Parameter.empty)
    return signature.replace(parameters=parameters[1:], return_annotation=return_annotation)
