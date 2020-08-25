import pytest
from ioc import (
    InvalidFunctionException,
    generate_function_factory,
)


def test_generate_sync_factory_from_function() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self, value: int) -> int:
            raise NotImplementedError()

    def test_function(value: int) -> int:
        return value + 1

    test_factory = generate_function_factory(TestFactory, test_function)
    assert test_factory(42) == 43


@pytest.mark.asyncio
async def test_generate_async_factory_from_function() -> None:
    class TestFactory:
        __slots__ = ()

        async def __call__(self, value: int) -> int:
            raise NotImplementedError()

    async def test_function(value: int) -> int:
        return value + 1

    test_factory = generate_function_factory(TestFactory, test_function)
    assert await test_factory(42) == 43


@pytest.mark.asyncio
async def test_generate_async_factory_from_sync_function() -> None:
    class TestFactory:
        __slots__ = ()

        async def __call__(self, value: int) -> int:
            raise NotImplementedError()

    def test_function(value: int) -> int:
        return value + 1

    with pytest.raises(InvalidFunctionException):
        generate_function_factory(TestFactory, test_function)


@pytest.mark.asyncio
async def test_generate_factory_from_not_a_function() -> None:
    class TestFactory:
        __slots__ = ()

        async def __call__(self) -> int:
            raise NotImplementedError()

    with pytest.raises(InvalidFunctionException):
        generate_function_factory(TestFactory, int)


def test_generate_factory_from_function_with_different_signature() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self, value: int) -> int:
            raise NotImplementedError()

    def test_function() -> int:
        return 42

    with pytest.raises(InvalidFunctionException):
        generate_function_factory(TestFactory, test_function)
