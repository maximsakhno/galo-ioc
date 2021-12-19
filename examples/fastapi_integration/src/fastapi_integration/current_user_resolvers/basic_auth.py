from typing import Callable, Awaitable
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ioc import get_factory, add_factory
from fastapi_integration.users.models import User, convert_private_user_to_user
from fastapi_integration.users.repositories import UserRepositoryFactory, UserNotFoundByLoginException
from fastapi_integration.current_user_resolvers import CurrentUserResolverFactory


__all__ = [
    "load",
]


def load() -> None:
    user_repository_factory = get_factory(UserRepositoryFactory)
    user_repository = user_repository_factory()
    security = HTTPBasic()

    async def resolve_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> User:
        try:
            private_user = await user_repository.get_by_login(credentials.username)
        except UserNotFoundByLoginException:
            raise HTTPException(status_code=401, detail="Invalid username or password") from None
        if not private_user.password == credentials.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return convert_private_user_to_user(private_user)

    class CurrentUserResolverFactoryImpl(CurrentUserResolverFactory):
        def __call__(self) -> Callable[..., Awaitable[User]]:
            return resolve_current_user

    add_factory(CurrentUserResolverFactory, CurrentUserResolverFactoryImpl())
