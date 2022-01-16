from uuid import UUID

from fastapi_integration.users.models import User, UserToCreate, UserToUpdate
from fastapi_integration.users.repositories import UserRepository, UserRepositoryFactory
from fastapi_integration.users.services import UserService, UserServiceFactory
from galo_ioc import add_factory, get_factory

__all__ = [
    "UserServiceImpl",
    "load",
]


class UserServiceImpl(UserService):
    def __init__(self, repository: UserRepository) -> None:
        self.__repository = repository

    async def create(self, user: UserToCreate) -> User:
        return await self.__repository.create(user)

    async def update(self, id: UUID, user: UserToUpdate) -> User:
        return await self.__repository.update(id, user)

    async def delete(self, id: UUID) -> User:
        return await self.__repository.delete(id)

    async def get_by_id(self, id: UUID) -> User:
        return await self.__repository.get_by_id(id)


def load() -> None:
    class UserServiceFactoryImpl(UserServiceFactory):
        def __call__(self) -> UserService:
            return service

    repository_factory = get_factory(UserRepositoryFactory)
    repository = repository_factory()
    service = UserServiceImpl(repository)
    add_factory(UserServiceFactory, UserServiceFactoryImpl())
