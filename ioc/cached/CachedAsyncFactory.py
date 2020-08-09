from typing import (
    TypeVar,
    Generic,
    Callable,
    Awaitable,
)
from asyncio import (
    Lock
)


__all__ = [
    "CachedAsyncFactory",
]


T = TypeVar("T", covariant=True)


class CachedAsyncFactory(Generic[T]):
    __slots__ = (
        "__factory",
        "__has_result",
        "__result",
        "__lock",
    )

    def __init__(self, factory: Callable[[], Awaitable[T]]) -> None:
        self.__factory = factory
        self.__has_result = False
        self.__result = None
        self.__lock = Lock()

    async def __call__(self) -> T:
        if not self.__has_result:
            async with self.__lock:
                if not self.__has_result:
                    self.__result = await self.__factory()
                    self.__has_result = True
        return self.__result
