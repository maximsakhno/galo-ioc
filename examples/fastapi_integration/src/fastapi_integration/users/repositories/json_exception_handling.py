from typing import Any

from fastapi_integration.json_exception_handlers import JsonExceptionHandlerFactory
from fastapi_integration.users.repositories import (
    UserAlreadyExistsException,
    UserNotFoundByIdException,
)
from galo_ioc import get_factory

__all__ = [
    "load",
]


def load() -> None:
    def get_detail_for_user_already_exists_exception(exception: UserAlreadyExistsException) -> Any:
        return {"login": exception.login}

    def get_detail_for_user_not_found(exception: UserNotFoundByIdException) -> Any:
        return {"id": str(exception.id)}

    exception_handler_factory = get_factory(JsonExceptionHandlerFactory)
    exception_handler = exception_handler_factory()
    exception_handler.register_exception(
        UserAlreadyExistsException, 409, get_detail_for_user_already_exists_exception
    )
    exception_handler.register_exception(
        UserNotFoundByIdException, 404, get_detail_for_user_not_found
    )
