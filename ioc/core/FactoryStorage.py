from typing import (
    TypeVar,
    Any,
    Callable,
    Collection,
)
from .Key import Key


__all__ = [
    "FactoryStorage",
]


F = TypeVar("F", bound=Callable)


class FactoryStorage:
    __slots__ = ()

    @property
    def keys(self) -> Collection[Key[Callable]]:
        raise NotImplementedError()

    def get_factory(self, key: Key[F]) -> F:
        raise NotImplementedError()

    def set_factory(self, key: Key[F], factory: F) -> None:
        raise NotImplementedError()
