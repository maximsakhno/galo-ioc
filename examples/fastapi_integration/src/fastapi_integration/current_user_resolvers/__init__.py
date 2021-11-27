from typing import Callable, Awaitable
from fastapi_integration.users.models import User


__all__ = [
    "CurrentUserResolverFactory",
]


class CurrentUserResolverFactory:
    def __call__(self) -> Callable[..., Awaitable[User]]:
        raise NotImplementedError()
