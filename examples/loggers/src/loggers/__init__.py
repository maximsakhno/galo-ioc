from typing import Optional
from logging import Logger


__all__ = [
    "LoggerFactory",
]


class LoggerFactory:
    def __call__(self, name: Optional[str] = None) -> Logger:
        raise NotImplementedError()
