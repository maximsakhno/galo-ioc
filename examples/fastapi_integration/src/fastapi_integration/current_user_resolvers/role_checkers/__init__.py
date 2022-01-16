from typing import Collection

from fastapi.requests import Request
from fastapi_integration.users.models import User

__all__ = [
    "RoleChecker",
    "RoleCheckerFactory",
]


class RoleChecker:
    def register_roles_for_route(self, method: str, path: str, roles: Collection[str]) -> None:
        raise NotImplementedError()

    def check_role(self, request: Request, user: User) -> None:
        raise NotImplementedError()


class RoleCheckerFactory:
    def __call__(self) -> RoleChecker:
        raise NotImplementedError()
