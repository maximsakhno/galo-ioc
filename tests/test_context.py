import pytest
from typing import Optional, Any
from unittest.mock import Mock, call
from ioc import FactoryType, Factory, FactoryContainerException, FactoryNotFoundException
from ioc.context import factory_container, add_factory, add_factory_decorator, get_factory


class FactoryForTest:
    def __call__(self, a: int, b: int) -> int:
        raise NotImplementedError()


class FactoryForTestImpl(FactoryForTest):
    def __init__(self, mock: Optional[Mock] = None) -> None:
        if mock is None:
            mock = Mock(side_effect=lambda a, b: a + b)
        self.mock = mock

    def __call__(self, a: int, b: int) -> int:
        return self.mock(a, b)


def test_add_factory_without_factory_container() -> None:
    with pytest.raises(FactoryContainerException):
        add_factory(FactoryForTest, FactoryForTestImpl())


def test_add_factory_with_factory_container() -> None:
    factory_for_test = FactoryForTestImpl()
    with factory_container():
        add_factory(FactoryForTest, factory_for_test)
        assert get_factory(FactoryForTest)(1, 2) == 3
    factory_for_test.mock.assert_called_once_with(1, 2)


def test_add_factory_with_nested_factory_container() -> None:
    factory_for_test1 = FactoryForTestImpl()
    factory_for_test2 = FactoryForTestImpl()
    with factory_container():
        add_factory(FactoryForTest, factory_for_test1)
        with factory_container():
            add_factory(FactoryForTest, factory_for_test2)
            get_factory(FactoryForTest)(1, 2)
            factory_for_test1.mock.assert_not_called()
            factory_for_test2.mock.assert_called_once_with(1, 2)
        factory_for_test2.mock.reset_mock()
        get_factory(FactoryForTest)(1, 2)
        factory_for_test1.mock.assert_called_once_with(1, 2)
        factory_for_test2.mock.assert_not_called()


def test_add_factory_decorator() -> None:
    def factory_decorator1(factory_type: FactoryType, id: Optional[str], factory: Factory) -> Factory:
        if not issubclass(factory_type, FactoryForTest):
            return factory

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            parent.before_mock1(*args, **kwargs)
            result = factory(*args, **kwargs)
            parent.after_mock1(*args, **kwargs)
            return result

        return wrapper

    def factory_decorator2(factory_type: FactoryType, id: Optional[str], factory: Factory) -> Factory:
        if not issubclass(factory_type, FactoryForTest):
            return factory

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            parent.before_mock2(*args, **kwargs)
            result = factory(*args, **kwargs)
            parent.after_mock2(*args, **kwargs)
            return result

        return wrapper

    factory_for_test = FactoryForTestImpl()
    parent = Mock()
    parent.mock = factory_for_test.mock
    parent.before_mock1 = Mock()
    parent.before_mock2 = Mock()
    parent.after_mock1 = Mock()
    parent.after_mock2 = Mock()

    with factory_container():
        add_factory_decorator(factory_decorator2)
        add_factory(FactoryForTest, factory_for_test)
        add_factory_decorator(factory_decorator1)
        assert get_factory(FactoryForTest)(1, 2) == 3

    parent.assert_has_calls([
        call.before_mock1(1, 2),
        call.before_mock2(1, 2),
        call.mock(1, 2),
        call.after_mock2(1, 2),
        call.after_mock1(1, 2),
    ])


def test_factory_not_found() -> None:
    with factory_container():
        with pytest.raises(FactoryNotFoundException):
            get_factory(FactoryForTest)(1, 2)


def test_non_callable_factory() -> None:
    class NonCallableFactory:
        pass

    with factory_container():
        with pytest.raises(FactoryContainerException):
            add_factory(NonCallableFactory, NonCallableFactory())


def test_factory_type_with_illegal_attributes() -> None:
    class FactoryWithIllegalAttributes:
        a: int = 1

        def __call__(self) -> None:
            pass

    with factory_container():
        with pytest.raises(FactoryContainerException):
            add_factory(FactoryWithIllegalAttributes, FactoryWithIllegalAttributes())
