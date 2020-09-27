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


__all__ = [
    "generate_singleton_factory",
]


F = TypeVar("F", bound=Callable)


SYNC_SINGLETON_STMT = """
class SingletonFactory(factory_type):
    __slots__ = (
        "__instance",
    )
    
    def __init__(self, instance: return_annotation) -> None:
        self.__instance = instance
    
    def __call__(self) -> return_annotation:
        return self.__instance
"""


ASYNC_SINGLETON_STMT = """
class SingletonFactory(factory_type):
    __slots__ = (
        "__instance",
    )
    
    def __init__(self, instance: return_annotation) -> None:
        self.__instance = instance
    
    async def __call__(self) -> return_annotation:
        return self.__instance
"""


def generate_singleton_factory(factory_type: Type[F], instance: Any) -> F:
    check_factory_type(factory_type)
    signature = Signature.from_callable(factory_type.__call__)
    type_hints = get_type_hints(factory_type.__call__)
    if len(signature.parameters) > 1:
        raise TypeError(factory_type, "Must not contain parameters.") from None
    try:
        return_annotation = type_hints["return"]
    except KeyError:
        raise TypeError(factory_type, "Return annotation is required.") from None
    if not isinstance(return_annotation, type):
        raise TypeError(factory_type, "Return annotation must be a class.") from None
    if not isinstance(instance, return_annotation):
        message = f"Object '{instance}' must be instance of '{return_annotation}'."
        raise TypeError(factory_type, message) from None
    globals = {"factory_type": factory_type, "return_annotation": return_annotation}
    if iscoroutinefunction(factory_type.__call__):
        singleton_stmt = ASYNC_SINGLETON_STMT
    else:
        singleton_stmt = SYNC_SINGLETON_STMT
    exec(singleton_stmt, globals)
    singleton_type = cast(type, globals["SingletonFactory"])
    getattr(singleton_type, "__init__").__annotations__ = {"instance": return_annotation}
    getattr(singleton_type, "__call__").__annotations__ = type_hints
    singleton = singleton_type(instance)
    return singleton
