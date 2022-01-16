from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

from fastapi_integration.users.models import (
    PrivateUser,
    User,
    UserToCreate,
    UserToUpdate,
    convert_private_user_to_user,
)
from fastapi_integration.users.repositories import (
    UserAlreadyExistsException,
    UserNotFoundByIdException,
    UserNotFoundByLoginException,
    UserRepository,
    UserRepositoryFactory,
)
from galo_ioc import add_factory

__all__ = [
    "InMemoryUserRepository",
]


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.__id_to_user: Dict[UUID, PrivateUser] = {}
        self.__login_to_user: Dict[str, PrivateUser] = {}
        self.__create_sync(
            UserToCreate(
                login="admin",
                password="admin",
                role="admin",
            )
        )
        self.__create_sync(
            UserToCreate(
                login="employee",
                password="employee",
                role="employee",
            )
        )

    async def create(self, user: UserToCreate) -> User:
        return self.__create_sync(user)

    def __create_sync(self, user: UserToCreate) -> User:
        if user.login in self.__login_to_user:
            raise UserAlreadyExistsException(user.login)

        now = datetime.now()
        private_user = PrivateUser(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            login=user.login,
            password=user.password,
            role=user.role,
        )
        self.__id_to_user[private_user.id] = private_user
        self.__login_to_user[private_user.login] = private_user
        return convert_private_user_to_user(private_user)

    async def update(self, id: UUID, user: UserToUpdate) -> User:
        try:
            private_user = self.__id_to_user[id]
        except KeyError:
            raise UserNotFoundByIdException(id) from None

        if user.login != private_user.login:
            del self.__login_to_user[private_user.login]
            self.__login_to_user[user.login] = private_user

        private_user.updated_at = datetime.now()
        private_user.login = user.login
        private_user.password = user.password
        private_user.role = user.role
        return convert_private_user_to_user(private_user)

    async def delete(self, id: UUID) -> User:
        try:
            private_user = self.__id_to_user.pop(id)
        except KeyError:
            raise UserNotFoundByIdException(id) from None
        del self.__login_to_user[private_user.login]
        return convert_private_user_to_user(private_user)

    async def get_by_id(self, id: UUID) -> User:
        try:
            private_user = self.__id_to_user[id]
        except KeyError:
            raise UserNotFoundByIdException(id) from None
        return convert_private_user_to_user(private_user)

    async def get_by_login(self, login: str) -> PrivateUser:
        try:
            return self.__login_to_user[login]
        except KeyError:
            raise UserNotFoundByLoginException(login) from None


def load() -> None:
    class InMemoryUserRepositoryFactory(UserRepositoryFactory):
        def __call__(self) -> UserRepository:
            return repository

    repository = InMemoryUserRepository()
    add_factory(UserRepositoryFactory, InMemoryUserRepositoryFactory())
