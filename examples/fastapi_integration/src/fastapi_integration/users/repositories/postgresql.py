from datetime import datetime
from uuid import UUID

from asyncpg import Record
from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool
from fastapi_integration.databases.postgresql import ConnectionPoolFactory
from fastapi_integration.users.models import (
    PrivateUser,
    User,
    UserToCreate,
    UserToUpdate,
)
from fastapi_integration.users.repositories import (
    UserAlreadyExistsException,
    UserNotFoundByIdException,
    UserNotFoundByLoginException,
    UserRepository,
    UserRepositoryFactory,
)
from galo_ioc import add_factory, get_factory

__all__ = [
    "PostgreSQLUserRepository",
]


class PostgreSQLUserRepository(UserRepository):
    def __init__(self, connection_pool: Pool) -> None:
        self.__connection_pool = connection_pool

    async def create(self, user: UserToCreate) -> User:
        query = """
            insert into "users" ("login", "password", "role")
            values ($1, $2, $3)
            returning "id", "created_at", "updated_at", "login", "role"
        """
        async with self.__connection_pool.acquire() as connection:
            try:
                record = await connection.fetchrow(query, user.login, user.password, user.role)
            except UniqueViolationError:
                raise UserAlreadyExistsException(user.login) from None
        return self.__record_to_user(record)

    async def update(self, id: UUID, user: UserToUpdate) -> User:
        query = """
            update "users"
            set "updated_at" = $1, "login" = $2, "password" = $3, "role" = $4
            where "id" = $5
            returning "id", "created_at", "updated_at", "login", "role"
        """
        async with self.__connection_pool.acquire() as connection:
            record = await connection.fetchrow(
                query, datetime.now(), user.login, user.password, user.role, id
            )
        if record is None:
            raise UserNotFoundByIdException(id)
        return self.__record_to_user(record)

    async def delete(self, id: UUID) -> User:
        query = """
            delete from "users"
            where "id" = $1
            returning "id", "created_at", "updated_at", "login", "role"
        """
        async with self.__connection_pool.acquire() as connection:
            record = await connection.fetchrow(query, id)
        if record is None:
            raise UserNotFoundByIdException(id)
        return self.__record_to_user(record)

    async def get_by_id(self, id: UUID) -> User:
        query = """
            select "id", "created_at", "updated_at", "login", "role" from "users"
            where "id" = $1
        """
        async with self.__connection_pool.acquire() as connection:
            record = await connection.fetchrow(query, id)
        if record is None:
            raise UserNotFoundByIdException(id)
        return self.__record_to_user(record)

    async def get_by_login(self, login: str) -> PrivateUser:
        query = """
            select "id", "created_at", "updated_at", "login", "password", "role" from "users"
            where "login" = $1
        """
        async with self.__connection_pool.acquire() as connection:
            record = await connection.fetchrow(query, login)
        if record is None:
            raise UserNotFoundByLoginException(login)
        return self.__record_to_private_user(record)

    @staticmethod
    def __record_to_user(record: Record) -> User:
        return User(
            id=record["id"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
            login=record["login"],
            role=record["role"],
        )

    @staticmethod
    def __record_to_private_user(record: Record) -> PrivateUser:
        return PrivateUser(
            id=record["id"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
            login=record["login"],
            password=record["password"],
            role=record["role"],
        )


def load() -> None:
    class PostgreSQLUserRepositoryFactory(UserRepositoryFactory):
        def __call__(self) -> UserRepository:
            return repository

    connection_pool_factory = get_factory(ConnectionPoolFactory)
    connection_pool = connection_pool_factory()

    repository = PostgreSQLUserRepository(connection_pool)
    add_factory(UserRepositoryFactory, PostgreSQLUserRepositoryFactory())
