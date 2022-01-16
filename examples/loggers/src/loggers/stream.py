import logging
import os
import sys
from typing import Optional

from galo_ioc import add_factory
from loggers import LoggerFactory

__all__ = [
    "load",
]


def load() -> None:
    class LoggerFactoryImpl(LoggerFactory):
        def __call__(self, name: Optional[str] = None) -> logging.Logger:
            return logging.getLogger(name)

    format = os.getenv(
        "LOGGING_FORMAT",
        "%(asctime)s - [%(levelname)s] - %(name)s - "
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    )
    level = os.getenv("LOGGING_LEVEL", "DEBUG")
    logging.basicConfig(format=format, stream=sys.stdout, level=level)
    add_factory(LoggerFactory, LoggerFactoryImpl())
