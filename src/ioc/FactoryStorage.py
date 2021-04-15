from typing import (
    Iterator,
)
from .types import (
    F,
)
from .Key import Key


__all__ = [
    "FactoryStorage",
]


class FactoryStorage:
    def __getitem__(self, key: Key[F]) -> F:
        raise NotImplementedError()

    def __setitem__(self, key: Key[F], factory: F) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: Key) -> None:
        raise NotImplementedError()

    def __contains__(self, key: Key) -> bool:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Key]:
        raise NotImplementedError()

    def __bool__(self) -> bool:
        raise NotImplementedError()
