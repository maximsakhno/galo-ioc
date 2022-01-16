import os

from asyncpg import create_pool
from asyncpg.pool import Pool
from fastapi_integration.app import AppFactory
from fastapi_integration.databases.postgresql import ConnectionPoolFactory
from galo_ioc import add_factory, get_factory

__all__ = [
    "load",
]


def load() -> None:
    class ConnectionPoolFactoryImpl(ConnectionPoolFactory):
        def __call__(self) -> Pool:
            return connection_pool

    dsn = os.getenv("POSTGRESQL_CONNECTION_POOL_DSN", "postgresql://test:test@localhost:5432/test")
    min_size = int(os.getenv("POSTGRESQL_CONNECTION_POOL_MIN_SIZE", "4"))
    max_size = int(os.getenv("POSTGRESQL_CONNECTION_POOL_MAX_SIZE", "16"))
    connection_pool = create_pool(dsn=dsn, min_size=min_size, max_size=max_size)
    add_factory(ConnectionPoolFactory, ConnectionPoolFactoryImpl())

    app_factory = get_factory(AppFactory)
    app = app_factory()

    @app.on_event("startup")
    async def init_connection_pool() -> None:
        await connection_pool

    @app.on_event("shutdown")
    async def close_connection_pool() -> None:
        await connection_pool.close()
