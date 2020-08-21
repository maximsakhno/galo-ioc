from typing import (
    TypeVar,
    Any,
    Callable,
    Type,
    get_type_hints,
    cast,
)
from inspect import (
    Signature,
    iscoroutinefunction,
)
from ..util import (
    check_factory_type,
)
from ..core import (
    InvalidFactoryTypeException,
)


__all__ = [
    "InvalidObjectTypeException",
    "generate_singleton",
]


F = TypeVar("F", bound=Callable)


class InvalidObjectTypeException(Exception):
    pass


SYNC_SINGLETON_STMT = """
class Singleton(factory_type):
    __slots__ = ()
    def __call__(self) -> return_annotation:
        return object
"""


ASYNC_SINGLETON_STMT = """
class Singleton(factory_type):
    __slots__ = ()
    async def __call__(self) -> return_annotation:
        return object
"""


def generate_singleton(factory_type: Type[F], object: Any) -> F:
    check_factory_type(factory_type)
    signature = Signature.from_callable(factory_type.__call__)
    type_hints = get_type_hints(factory_type.__call__)
    if len(signature.parameters) > 1:
        raise InvalidFactoryTypeException(factory_type, "Must not contain parameters.") from None
    try:
        return_annotation = type_hints["return"]
    except KeyError:
        raise InvalidFactoryTypeException(factory_type, "Return annotation is required.") from None
    if not isinstance(return_annotation, type):
        raise InvalidFactoryTypeException(factory_type, "Return annotation must be a class.") from None
    if not isinstance(object, return_annotation):
        message = f"Object '{object}' must be instance of '{return_annotation}'."
        raise InvalidObjectTypeException(factory_type, message) from None
    globals = {"factory_type": factory_type, "return_annotation": return_annotation, "object": object}
    if iscoroutinefunction(factory_type.__call__):
        singleton_stmt = ASYNC_SINGLETON_STMT
    else:
        singleton_stmt = SYNC_SINGLETON_STMT
    exec(singleton_stmt, globals)
    singleton_type = cast(type, globals["Singleton"])
    singleton_type.__call__.__annotations__ = type_hints
    singleton = singleton_type()
    return singleton
