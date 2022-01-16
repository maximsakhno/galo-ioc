from fastapi import FastAPI

__all__ = [
    "AppFactory",
]


class AppFactory:
    def __call__(self) -> FastAPI:
        raise NotImplementedError()
