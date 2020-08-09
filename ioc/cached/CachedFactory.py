from typing import (
    TypeVar,
    Generic,
    Callable,
)
from threading import Lock


__all__ = [
    "CachedFactory",
]


T = TypeVar("T", covariant=True)


class CachedFactory(Generic[T]):
    __slots__ = (
        "__factory",
        "__has_result",
        "__result",
        "__lock",
    )

    def __init__(self, factory: Callable[[], T]) -> None:
        self.__factory = factory
        self.__has_result = False
        self.__result = None
        self.__lock = Lock()

    def __call__(self) -> T:
        if not self.__has_result:
            with self.__lock:
                if not self.__has_result:
                    self.__result = self.__factory()
                    self.__has_result = True
        return self.__result
