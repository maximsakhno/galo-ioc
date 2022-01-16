import logging
import os
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
    filename = os.getenv("LOGGING_FILE_NAME", "output.log")
    level = os.getenv("LOGGING_LEVEL", "DEBUG")
    logging.basicConfig(format=format, filename=filename, level=level)
    add_factory(LoggerFactory, LoggerFactoryImpl())
