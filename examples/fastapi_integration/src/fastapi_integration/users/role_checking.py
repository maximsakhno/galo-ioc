from ioc import get_factory
from fastapi_integration.current_user_resolvers.role_checkers import RoleCheckerFactory


__all__ = [
    "load",
]


def load() -> None:
    role_checker_factory = get_factory(RoleCheckerFactory)
    role_checker = role_checker_factory()
    role_checker.register_roles_for_route("POST", "/users", ["admin"])
    role_checker.register_roles_for_route("PUT", "/users/{id}", ["admin"])
    role_checker.register_roles_for_route("DELETE", "/users/{id}", ["admin"])
    role_checker.register_roles_for_route("GET", "/users/{id}", ["admin"])
    role_checker.register_roles_for_route("GET", "/whoami", ["admin", "employee"])
