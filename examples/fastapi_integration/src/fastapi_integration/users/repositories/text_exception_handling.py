from fastapi_integration.text_exception_handlers import TextExceptionHandlerFactory
from fastapi_integration.users.repositories import (
    UserAlreadyExistsException,
    UserNotFoundByIdException,
)
from galo_ioc import get_factory

__all__ = [
    "load",
]


def load() -> None:
    def get_message_for_user_already_exists_exception(exception: UserAlreadyExistsException) -> str:
        return f"User already exists: login={exception.login}"

    def get_message_for_user_not_found(exception: UserNotFoundByIdException) -> str:
        return f"User not found: id={exception.id}"

    exception_handler_factory = get_factory(TextExceptionHandlerFactory)
    exception_handler = exception_handler_factory()
    exception_handler.register_exception(
        UserAlreadyExistsException, 409, get_message_for_user_already_exists_exception
    )
    exception_handler.register_exception(
        UserNotFoundByIdException, 404, get_message_for_user_not_found
    )
