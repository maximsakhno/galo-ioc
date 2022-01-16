from typing import Callable, Type, TypeVar

from fastapi.requests import Request
from fastapi.responses import Response

__all__ = [
    "E",
    "TextExceptionHandler",
    "TextExceptionHandlerFactory",
]


E = TypeVar("E", bound=Exception)


class TextExceptionHandler:
    def register_exception(
        self,
        exception_type: Type[E],
        status_code: int,
        get_message: Callable[[E], str],
    ) -> None:
        raise NotImplementedError()

    async def __call__(self, request: Request, exception: Exception) -> Response:
        raise NotImplementedError()


class TextExceptionHandlerFactory:
    def __call__(self) -> TextExceptionHandler:
        raise NotImplementedError()
