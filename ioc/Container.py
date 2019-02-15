from typing import Any
from typing import Callable
from typing import Dict


__all__ = [
    "Container",
]


class Container:
    __slots__ = (
        "__strategies",
    )

    def __init__(self) -> None:
        self.__strategies: Dict[Any, Callable[..., Any]] = {}

    def __setitem__(self, key: Any, strategy: Callable[..., Any]) -> None:
        self.__strategies[key] = strategy

    def __getitem__(self, key: Any) -> Callable[..., Any]:
        return self.__strategies[key]
