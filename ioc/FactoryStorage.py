from typing import (
    TypeVar,
    Any,
    Callable,
    Iterator,
)
from .Key import Key


__all__ = [
    "FactoryStorage",
]


F = TypeVar("F", bound=Callable)


class FactoryStorage:
    def __getitem__(self, key: Key[F]) -> F:
        raise NotImplementedError()

    def __setitem__(self, key: Key[F], factory: F) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: Key[Any]) -> None:
        raise NotImplementedError()

    def __contains__(self, key: Key[Any]) -> bool:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Key[Any]]:
        raise NotImplementedError()

    def __bool__(self) -> bool:
        raise NotImplementedError()
