from uuid import UUID

from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from fastapi_integration.app import AppFactory
from fastapi_integration.current_user_resolvers import CurrentUserResolverFactory
from fastapi_integration.users.models import User, UserToCreate, UserToUpdate
from fastapi_integration.users.services import UserServiceFactory
from galo_ioc import get_factory

__all__ = [
    "load",
]


def load() -> None:
    app_factory = get_factory(AppFactory)
    app = app_factory()
    current_user_resolver_factory = get_factory(CurrentUserResolverFactory)
    current_user_resolver = current_user_resolver_factory()
    service_factory = get_factory(UserServiceFactory)
    service = service_factory()
    router = APIRouter(dependencies=[Depends(current_user_resolver)])

    @router.post("/users")
    async def create_user(user: UserToCreate) -> User:
        return await service.create(user)

    @router.put("/users/{id}")
    async def update_user(id: UUID, user: UserToUpdate) -> User:
        return await service.update(id, user)

    @router.delete("/users/{id}")
    async def delete_user(id: UUID) -> User:
        return await service.delete(id)

    @router.get("/users/{id}")
    async def get_user_by_id(id: UUID) -> User:
        return await service.get_by_id(id)

    @router.get("/whoami")
    async def get_current_user(user: User = Depends(current_user_resolver)) -> User:
        return user

    app.include_router(router)
