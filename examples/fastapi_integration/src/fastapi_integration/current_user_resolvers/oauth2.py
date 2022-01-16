from typing import Awaitable, Callable, Dict

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_integration.app import AppFactory
from fastapi_integration.current_user_resolvers import CurrentUserResolverFactory
from fastapi_integration.token_encoders import TokenEncoderFactory
from fastapi_integration.users.models import User
from fastapi_integration.users.repositories import (
    UserNotFoundByLoginException,
    UserRepositoryFactory,
)
from galo_ioc import add_factory, get_factory

__all__ = [
    "load",
]


def load() -> None:
    app_factory = get_factory(AppFactory)
    app = app_factory()

    token_encoder_factory = get_factory(TokenEncoderFactory)
    token_encoder = token_encoder_factory()

    user_repository_factory = get_factory(UserRepositoryFactory)
    user_repository = user_repository_factory()

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    async def resolve_current_user(token: str = Depends(oauth2_scheme)) -> User:
        user_id = token_encoder.decode(token)
        user = await user_repository.get_by_id(user_id)
        return user

    class CurrentUserResolverFactoryImpl(CurrentUserResolverFactory):
        def __call__(self) -> Callable[..., Awaitable[User]]:
            return resolve_current_user

    add_factory(CurrentUserResolverFactory, CurrentUserResolverFactoryImpl())

    @app.post("/login")
    async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
        try:
            user = await user_repository.get_by_login(form_data.username)
        except UserNotFoundByLoginException:
            raise HTTPException(status_code=401, detail="Invalid username or password") from None
        if form_data.password != user.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = token_encoder.encode(user.id)
        return {"access_token": token, "token_type": "bearer"}
