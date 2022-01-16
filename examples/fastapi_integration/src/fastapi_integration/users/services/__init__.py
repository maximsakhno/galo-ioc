from uuid import UUID

from fastapi_integration.users.models import User, UserToCreate, UserToUpdate

__all__ = [
    "UserServiceException",
    "UserService",
    "UserServiceFactory",
]


class UserServiceException(Exception):
    pass


class UserService:
    async def create(self, user: UserToCreate) -> User:
        raise NotImplementedError()

    async def update(self, id: UUID, user: UserToUpdate) -> User:
        raise NotImplementedError()

    async def delete(self, id: UUID) -> User:
        raise NotImplementedError()

    async def get_by_id(self, id: UUID) -> User:
        raise NotImplementedError()


class UserServiceFactory:
    def __call__(self) -> UserService:
        raise NotImplementedError()
