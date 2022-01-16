from uuid import UUID

from fastapi_integration.users.models import (
    PrivateUser,
    User,
    UserToCreate,
    UserToUpdate,
)

__all__ = [
    "UserRepositoryException",
    "UserAlreadyExistsException",
    "UserNotFoundByIdException",
    "UserNotFoundByLoginException",
    "UserRepository",
    "UserRepositoryFactory",
]


class UserRepositoryException(Exception):
    pass


class UserAlreadyExistsException(UserRepositoryException):
    def __init__(self, login: str) -> None:
        self.login = login


class UserNotFoundByIdException(UserRepositoryException):
    def __init__(self, id: UUID) -> None:
        self.id = id


class UserNotFoundByLoginException(UserRepositoryException):
    def __init__(self, login: str) -> None:
        self.login = login


class UserRepository:
    async def create(self, user: UserToCreate) -> User:
        raise NotImplementedError()

    async def update(self, id: UUID, user: UserToUpdate) -> User:
        raise NotImplementedError()

    async def delete(self, id: UUID) -> User:
        raise NotImplementedError()

    async def get_by_id(self, id: UUID) -> User:
        raise NotImplementedError()

    async def get_by_login(self, login: str) -> PrivateUser:
        raise NotImplementedError()


class UserRepositoryFactory:
    def __call__(self) -> UserRepository:
        raise NotImplementedError()
