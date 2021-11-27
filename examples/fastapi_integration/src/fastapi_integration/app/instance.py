from fastapi import FastAPI
from ioc.context import add_factory
from fastapi_integration.app import AppFactory


__all__ = [
    "load",
]


def load() -> None:
    class AppFactoryImpl(AppFactory):
        def __call__(self) -> FastAPI:
            return app

    app = FastAPI()
    add_factory(AppFactory, AppFactoryImpl())
