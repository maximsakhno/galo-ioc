from typing import Any, Optional
from unittest.mock import Mock, call

import pytest
from galo_ioc import (
    Factory,
    FactoryAlreadyAddedException,
    FactoryContainerImpl,
    FactoryNotFoundException,
    FactoryType,
    NoFactoryContainerInContextException,
    add_factory,
    add_factory_decorator,
    get_factory,
)


class TestFactory:
    def __call__(self, a: int, b: int) -> int:
        raise NotImplementedError()


class TestFactoryImpl(TestFactory):
    def __init__(self, mock: Optional[Mock] = None) -> None:
        if mock is None:
            mock = Mock(side_effect=lambda a, b: a + b)
        self.mock = mock

    def __call__(self, a: int, b: int) -> int:
        return self.mock(a, b)


def test_add_factory_without_factory_container() -> None:
    with pytest.raises(NoFactoryContainerInContextException):
        add_factory(TestFactory, TestFactoryImpl())


def test_add_factory_with_factory_container() -> None:
    test_factory = TestFactoryImpl()
    with FactoryContainerImpl():
        add_factory(TestFactory, test_factory)
        assert get_factory(TestFactory)(1, 2) == 3
    test_factory.mock.assert_called_once_with(1, 2)


def test_add_factory_when_factory_already_added() -> None:
    with FactoryContainerImpl():
        add_factory(TestFactory, TestFactoryImpl())
        with pytest.raises(FactoryAlreadyAddedException):
            add_factory(TestFactory, TestFactoryImpl())


def test_add_factory_with_nested_factory_container() -> None:
    test_factory1 = TestFactoryImpl()
    test_factory2 = TestFactoryImpl()
    with FactoryContainerImpl():
        add_factory(TestFactory, test_factory1)
        with FactoryContainerImpl():
            add_factory(TestFactory, test_factory2)
            get_factory(TestFactory)(1, 2)
            test_factory1.mock.assert_not_called()
            test_factory2.mock.assert_called_once_with(1, 2)
        test_factory2.mock.reset_mock()
        get_factory(TestFactory)(1, 2)
        test_factory1.mock.assert_called_once_with(1, 2)
        test_factory2.mock.assert_not_called()


def test_add_factory_decorator() -> None:
    def factory_decorator1(
        factory_type: FactoryType,
        id: Optional[str],
        factory: Factory,
    ) -> Factory:
        if not issubclass(factory_type, TestFactory):
            return factory

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            parent.before_mock1(*args, **kwargs)
            result = factory(*args, **kwargs)
            parent.after_mock1(*args, **kwargs)
            return result

        return wrapper

    def factory_decorator2(
        factory_type: FactoryType,
        id: Optional[str],
        factory: Factory,
    ) -> Factory:
        if not issubclass(factory_type, TestFactory):
            return factory

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            parent.before_mock2(*args, **kwargs)
            result = factory(*args, **kwargs)
            parent.after_mock2(*args, **kwargs)
            return result

        return wrapper

    test_factory = TestFactoryImpl()
    parent = Mock()
    parent.mock = test_factory.mock
    parent.before_mock1 = Mock()
    parent.before_mock2 = Mock()
    parent.after_mock1 = Mock()
    parent.after_mock2 = Mock()

    with FactoryContainerImpl():
        add_factory_decorator(factory_decorator2)
        add_factory(TestFactory, test_factory)
        add_factory_decorator(factory_decorator1)
        assert get_factory(TestFactory)(1, 2) == 3

    parent.assert_has_calls(
        [
            call.before_mock1(1, 2),
            call.before_mock2(1, 2),
            call.mock(1, 2),
            call.after_mock2(1, 2),
            call.after_mock1(1, 2),
        ]
    )


def test_get_factory_without_factory_container() -> None:
    with pytest.raises(NoFactoryContainerInContextException):
        get_factory(TestFactory)(1, 2)


def test_factory_not_found() -> None:
    with FactoryContainerImpl():
        with pytest.raises(FactoryNotFoundException):
            get_factory(TestFactory)(1, 2)


def test_non_callable_factory() -> None:
    class NonCallableFactory:
        pass

    with FactoryContainerImpl():
        with pytest.raises(Exception):
            add_factory(NonCallableFactory, NonCallableFactory())


def test_factory_type_with_illegal_attributes() -> None:
    class FactoryWithIllegalAttributes:
        a: int = 1

        def __call__(self) -> None:
            pass

    with FactoryContainerImpl():
        with pytest.raises(Exception):
            add_factory(FactoryWithIllegalAttributes, FactoryWithIllegalAttributes())
