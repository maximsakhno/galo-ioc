from typing import (
    TypeVar,
    Optional,
    Callable,
    Any,
    Type,
)


__all__ = [
    "FactoryContainer",
]


F = TypeVar("F", bound=Callable)


class FactoryContainer:
    __slots__ = ()

    def get_factory(self, factory_type: Type[F], id: Optional[Any] = None) -> F:
        raise NotImplementedError()

    def set_factory(self, factory_type: Type[F], factory: F, id: Optional[Any] = None) -> None:
        raise NotImplementedError()
