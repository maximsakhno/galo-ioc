from typing import Any, Callable, Dict, Type

from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_integration.app import AppFactory
from fastapi_integration.json_exception_handlers import (
    E,
    JsonExceptionHandler,
    JsonExceptionHandlerFactory,
)
from galo_ioc import add_factory, get_factory

__all__ = [
    "JsonExceptionHandlerImpl",
    "load",
]


class JsonExceptionHandlerImpl(JsonExceptionHandler):
    def __init__(self, default_status_code: int = 500) -> None:
        self.__default_status_code = default_status_code
        self.__exception_type_to_status_code: Dict[Type[Exception], int] = {}
        self.__exception_type_to_get_detail: Dict[Type[Exception], Callable[[Exception], Any]] = {}

    def register_exception(
        self,
        exception_type: Type[E],
        status_code: int,
        get_detail: Callable[[E], Any],
    ) -> None:
        self.__exception_type_to_status_code[exception_type] = status_code
        self.__exception_type_to_get_detail[exception_type] = get_detail

    async def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        if isinstance(exception, RequestValidationError):
            return await request_validation_exception_handler(request, exception)

        if isinstance(exception, HTTPException):
            return await http_exception_handler(request, exception)

        exception_type = type(exception)
        status_code = self.__exception_type_to_status_code.get(
            exception_type, self.__default_status_code
        )
        try:
            get_detail = self.__exception_type_to_get_detail[exception_type]
        except KeyError:
            return JSONResponse(status_code=status_code, content={"detail": None})
        else:
            detail = get_detail(exception)
            return JSONResponse(status_code=status_code, content={"detail": detail})


def load() -> None:
    class JsonExceptionHandlerFactoryImpl(JsonExceptionHandlerFactory):
        def __call__(self) -> JsonExceptionHandler:
            return exception_handler

    exception_handler = JsonExceptionHandlerImpl()
    add_factory(JsonExceptionHandlerFactory, JsonExceptionHandlerFactoryImpl())

    app_factory = get_factory(AppFactory)
    app = app_factory()
    app.add_exception_handler(Exception, exception_handler.__call__)
