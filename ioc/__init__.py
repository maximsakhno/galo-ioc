from .Container import Container
from .strategies import Singleton


__all__ = [
    "IOC",
    "Singleton",
]


IOC: Container = Container()
