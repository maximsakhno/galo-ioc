from logging import Logger
from typing import Optional

__all__ = [
    "LoggerFactory",
]


class LoggerFactory:
    def __call__(self, name: Optional[str] = None) -> Logger:
        raise NotImplementedError()
