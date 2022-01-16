from fastapi_integration.current_user_resolvers.role_checkers import RoleCheckerFactory
from galo_ioc import get_factory

__all__ = [
    "load",
]


def load() -> None:
    role_checker_factory = get_factory(RoleCheckerFactory)
    role_checker = role_checker_factory()
    role_checker.register_roles_for_route("POST", "/happy_birthday", ["admin"])
