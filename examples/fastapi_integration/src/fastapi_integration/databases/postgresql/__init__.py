from asyncpg.pool import Pool

__all__ = [
    "ConnectionPoolFactory",
]


class ConnectionPoolFactory:
    def __call__(self) -> Pool:
        raise NotImplementedError()
