import pytest
from typing import (
    NoReturn,
)
from ioc import (
    CachedAsyncFactory,
)


@pytest.mark.asyncio
async def test_getting_instance() -> None:
    async def f() -> object:
        return object()

    factory = CachedAsyncFactory(f)
    instance1 = await factory()
    instance2 = await factory()
    assert instance1 is instance2


@pytest.mark.asyncio
async def test_raising_exception() -> None:
    async def f() -> NoReturn:
        raise Exception()

    factory = CachedAsyncFactory(f)

    with pytest.raises(Exception):
        await factory()
