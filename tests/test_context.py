import pytest
from unittest.mock import (
    Mock,
    AsyncMock,
)
from ioc import (
    FactoryContainerNotSetException,
    FactoryNotFoundException,
    DictFactoryContainer,
    using_factory_container,
    get_factory,
    use_factory,
)


class TestFactory:
    __slots__ = ()

    def __call__(self) -> int:
        raise NotImplementedError()


def test_calling_factory_proxy_out_of_factory_container_context() -> None:
    test_factory = get_factory(TestFactory)

    with pytest.raises(FactoryContainerNotSetException):
        test_factory()


def test_calling_factory_proxy_inside_factory_container_context() -> None:
    test_factory, set_test_factory = use_factory(TestFactory)

    with using_factory_container(DictFactoryContainer()):
        with pytest.raises(FactoryNotFoundException):
            test_factory()

        set_test_factory(Mock(TestFactory, return_value=42))
        assert test_factory() == 42


def test_calling_factory_proxy_inside_different_factory_container_contexts() -> None:
    test_factory, set_test_factory = use_factory(TestFactory)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory(Mock(TestFactory, return_value=42))

    with using_factory_container(DictFactoryContainer()):
        with pytest.raises(FactoryNotFoundException):
            test_factory()


def test_nested_factory_container_context() -> None:
    test_factory, set_test_factory = use_factory(TestFactory)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory(Mock(TestFactory, return_value=1))

        with using_factory_container(DictFactoryContainer()):
            assert test_factory() == 1

            set_test_factory(Mock(TestFactory, return_value=2))
            assert test_factory() == 2

        assert test_factory() == 1


def test_different_factory_proxies_with_the_same_factory_type() -> None:
    test_factory1, set_test_factory1 = use_factory(TestFactory)
    test_factory2, set_test_factory2 = use_factory(TestFactory)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory1(Mock(TestFactory, return_value=1))

        with pytest.raises(FactoryNotFoundException):
            test_factory2()

        set_test_factory2(Mock(TestFactory, return_value=2))

        assert test_factory1() == 1
        assert test_factory2() == 2


def test_factory_with_different_argument_kinds_proxy() -> None:
    class TestFactoryWithDifferentArgumentKinds:
        __slots__ = ()

        def __call__(self, a: int, /, b: int, *, c: int = 3) -> int:
            raise NotImplementedError()

    test_factory_mock = Mock(TestFactoryWithDifferentArgumentKinds, return_value=42)
    test_factory, set_test_factory = use_factory(TestFactoryWithDifferentArgumentKinds)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory(test_factory_mock)
        assert test_factory(1, 2) == 42

    test_factory_mock.assert_called_once_with(1, 2, c=3)


def test_factory_with_variadic_arguments_proxy() -> None:
    class TestFactoryWithVariadicArguments:
        __slots__ = ()

        def __call__(self, *args: int, **kwargs: int) -> int:
            raise NotImplementedError()

    test_factory_mock = Mock(TestFactoryWithVariadicArguments, return_value=42)
    test_factory, set_test_factory = use_factory(TestFactoryWithVariadicArguments)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory(test_factory_mock)
        assert test_factory(1, b=2) == 42

    test_factory_mock.assert_called_once_with(1, b=2)


def test_factory_with_positional_only_arguments_proxy() -> None:
    class TestFactoryWithPositionalOnlyArguments:
        __slots__ = ()

        def __call__(self, a: int, /) -> int:
            raise NotImplementedError()

    test_factory_mock = Mock(TestFactoryWithPositionalOnlyArguments, return_value=42)
    test_factory, set_test_factory = use_factory(TestFactoryWithPositionalOnlyArguments)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory(test_factory_mock)
        assert test_factory(1) == 42

    test_factory_mock.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_async_factory_proxy() -> None:
    class TestAsyncFactory:
        __slots__ = ()

        async def __call__(self) -> int:
            raise NotImplementedError()

    test_factory_mock = AsyncMock(TestAsyncFactory, return_value=42)
    test_factory, set_test_factory = use_factory(TestAsyncFactory)

    with using_factory_container(DictFactoryContainer()):
        set_test_factory(test_factory_mock)
        assert await test_factory() == 42

    test_factory_mock.assert_awaited_once()
