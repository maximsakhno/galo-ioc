import pytest
from typing import (
    Optional,
)
from ioc import (
    InvalidFactoryTypeException,
    InvalidObjectTypeException,
    generate_singleton_factory,
)


def test_sync_singleton() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self) -> int:
            raise NotImplementedError()

    forty_two = 42
    test_factory = generate_singleton_factory(TestFactory, forty_two)
    assert test_factory() is forty_two


@pytest.mark.asyncio
async def test_async_singleton() -> None:
    class TestFactory:
        __slots__ = ()

        async def __call__(self) -> int:
            raise NotImplementedError()

    forty_two = 42
    test_factory = generate_singleton_factory(TestFactory, forty_two)
    assert await test_factory() is forty_two


@pytest.mark.asyncio
async def test_factory_type_with_parameters() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self, a: int) -> int:
            raise NotImplementedError()

    with pytest.raises(InvalidFactoryTypeException):
        generate_singleton_factory(TestFactory, 42)


@pytest.mark.asyncio
async def test_factory_type_without_return_annotation() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self):
            raise NotImplementedError()

    with pytest.raises(InvalidFactoryTypeException):
        generate_singleton_factory(TestFactory, 42)


def test_factory_type_with_not_a_class_return_annotation() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self) -> Optional[int]:
            raise NotImplementedError()

    with pytest.raises(InvalidFactoryTypeException):
        generate_singleton_factory(TestFactory, 42)


def test_mismatch_object_type_and_return_annotation() -> None:
    class TestFactory:
        __slots__ = ()

        def __call__(self) -> int:
            raise NotImplementedError()

    with pytest.raises(InvalidObjectTypeException):
        generate_singleton_factory(TestFactory, "42")
