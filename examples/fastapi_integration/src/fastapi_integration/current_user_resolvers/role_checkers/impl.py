from enum import Enum, auto
from typing import Awaitable, Callable, Collection, Iterable, Optional

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.requests import Request
from fastapi_integration.current_user_resolvers import CurrentUserResolverFactory
from fastapi_integration.current_user_resolvers.role_checkers import (
    RoleChecker,
    RoleCheckerFactory,
)
from fastapi_integration.users.models import User
from galo_ioc import (
    Factory,
    FactoryType,
    add_factory,
    add_factory_decorator,
    get_factory,
)

__all__ = [
    "RoleCheckerImpl",
    "load",
]


class Keys(Enum):
    PARAMETER = auto()
    ROLES = auto()


class RoleCheckerImpl(RoleChecker):
    def __init__(self) -> None:
        self.__role_info: dict = {}

    def register_roles_for_route(self, method: str, path: str, roles: Collection[str]) -> None:
        role_info = self.__get_role_info_by_method(method)
        for path_item in self.__get_path_items(path):
            if path_item.startswith("{") and path_item.endswith("}"):
                role_info[Keys.PARAMETER] = {}
                role_info = role_info[Keys.PARAMETER]
            else:
                role_info[path_item] = {}
                role_info = role_info[path_item]
        role_info[Keys.ROLES] = roles

    def check_role(self, request: Request, user: User) -> None:
        method = request.method
        path = request.url.path
        role_info = self.__get_role_info_by_method(method)
        for path_item in self.__get_path_items(path):
            try:
                role_info = role_info[path_item]
            except KeyError:
                try:
                    role_info = role_info[Keys.PARAMETER]
                except KeyError:
                    return
        try:
            roles = role_info[Keys.ROLES]
        except KeyError:
            return
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Invalid role")

    def __get_role_info_by_method(self, method: str) -> dict:
        try:
            return self.__role_info[method]
        except KeyError:
            self.__role_info[method] = {}
            return self.__role_info[method]

    @staticmethod
    def __get_path_items(path: str) -> Iterable[str]:
        for path_item in path.split("/"):
            if not path_item:
                continue
            yield path_item


def load() -> None:
    current_user_resolver_factory = get_factory(CurrentUserResolverFactory)
    current_user_resolver = current_user_resolver_factory()

    class FastAPIRoleChecker(RoleCheckerImpl):
        async def __call__(
            self,
            request: Request,
            user: User = Depends(current_user_resolver),
        ) -> User:
            self.check_role(request, user)
            return user

    class RoleCheckerFactoryImpl(RoleCheckerFactory):
        def __call__(self) -> RoleChecker:
            return role_checker

    class RoleCheckerCurrentUserResolverFactory(CurrentUserResolverFactory):
        def __call__(self) -> Callable[..., Awaitable[User]]:
            return role_checker

    def factory_decorator(
        factory_type: FactoryType,
        id: Optional[str],
        factory: Factory,
    ) -> Factory:
        if not issubclass(factory_type, CurrentUserResolverFactory):
            return factory
        return RoleCheckerCurrentUserResolverFactory()

    role_checker = FastAPIRoleChecker()
    add_factory(RoleCheckerFactory, RoleCheckerFactoryImpl())
    add_factory_decorator(factory_decorator)
