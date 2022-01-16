from typing import Any, Callable, Dict, Type

from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse, Response
from fastapi_integration.app import AppFactory
from fastapi_integration.text_exception_handlers import (
    E,
    TextExceptionHandler,
    TextExceptionHandlerFactory,
)
from galo_ioc import add_factory, get_factory

__all__ = [
    "TextExceptionHandlerImpl",
    "load",
]


class TextExceptionHandlerImpl(TextExceptionHandler):
    def __init__(self, default_status_code: int = 500) -> None:
        self.__default_status_code = default_status_code
        self.__exception_type_to_status_code: Dict[Type[Exception], int] = {}
        self.__exception_type_to_get_message: Dict[Type[Exception], Callable[[Exception], Any]] = {}

    def register_exception(
        self,
        exception_type: Type[E],
        status_code: int,
        get_message: Callable[[E], str],
    ) -> None:
        self.__exception_type_to_status_code[exception_type] = status_code
        self.__exception_type_to_get_message[exception_type] = get_message

    async def __call__(self, request: Request, exception: Exception) -> Response:
        if isinstance(exception, RequestValidationError):
            return await request_validation_exception_handler(request, exception)

        if isinstance(exception, HTTPException):
            return await http_exception_handler(request, exception)

        exception_type = type(exception)
        status_code = self.__exception_type_to_status_code.get(
            exception_type, self.__default_status_code
        )
        try:
            get_message = self.__exception_type_to_get_message[exception_type]
        except KeyError:
            return PlainTextResponse(status_code=status_code)
        else:
            message = get_message(exception)
            return PlainTextResponse(status_code=status_code, content=message)


def load() -> None:
    class TextExceptionHandlerFactoryImpl(TextExceptionHandlerFactory):
        def __call__(self) -> TextExceptionHandler:
            return exception_handler

    exception_handler = TextExceptionHandlerImpl()
    add_factory(TextExceptionHandlerFactory, TextExceptionHandlerFactoryImpl())

    app_factory = get_factory(AppFactory)
    app = app_factory()
    app.add_exception_handler(Exception, exception_handler.__call__)
