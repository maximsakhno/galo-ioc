from typing import Any


__all__ = [
    "Singleton",
]


class Singleton:
    __slots__ = (
        "__instance",
    )

    def __init__(self, instance: Any) -> None:
        self.__instance: Any = instance

    def __call__(self) -> Any:
        return self.__instance
