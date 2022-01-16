from fastapi import FastAPI
from fastapi_integration.app import AppFactory
from galo_ioc import add_factory

__all__ = [
    "load",
]


def load() -> None:
    class AppFactoryImpl(AppFactory):
        def __call__(self) -> FastAPI:
            return app

    app = FastAPI()
    add_factory(AppFactory, AppFactoryImpl())
