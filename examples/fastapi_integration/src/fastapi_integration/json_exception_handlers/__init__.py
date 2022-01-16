from typing import Any, Callable, Type, TypeVar

from fastapi.requests import Request
from fastapi.responses import JSONResponse

__all__ = [
    "E",
    "JsonExceptionHandler",
    "JsonExceptionHandlerFactory",
]


E = TypeVar("E", bound=Exception)


class JsonExceptionHandler:
    def register_exception(
        self,
        exception_type: Type[E],
        status_code: int,
        get_detail: Callable[[E], Any],
    ) -> None:
        raise NotImplementedError()

    async def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        raise NotImplementedError()


class JsonExceptionHandlerFactory:
    def __call__(self) -> JsonExceptionHandler:
        raise NotImplementedError()
