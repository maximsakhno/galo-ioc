import pytest
from ioc import (
    InvalidFactoryTypeException,
    InvalidFactoryException,
    FactoryNotFoundException,
    DictFactoryContainer,
)


class SomeFactory:
    __slots__ = ()

    def __call__(self) -> int:
        raise NotImplementedError()


class SomeFactoryStub(SomeFactory):
    __slots__ = (
        "__value",
    )

    def __init__(self, value: int) -> None:
        self.__value = value

    def __call__(self) -> int:
        return self.__value


def test_getting_existing_factory() -> None:
    container = DictFactoryContainer()
    container.set_factory(SomeFactory, SomeFactoryStub(42))
    assert container.get_factory(SomeFactory)() == 42


def test_getting_missing_factory() -> None:
    container = DictFactoryContainer()

    with pytest.raises(FactoryNotFoundException):
        container.get_factory(SomeFactory)


def test_getting_factory_by_id() -> None:
    container = DictFactoryContainer()
    container.set_factory(SomeFactory, SomeFactoryStub(42), "id1")

    with pytest.raises(FactoryNotFoundException):
        container.get_factory(SomeFactory)

    with pytest.raises(FactoryNotFoundException):
        container.get_factory(SomeFactory, "id2")

    assert container.get_factory(SomeFactory, "id1")() == 42


def test_setting_factory_invalid_attributes() -> None:
    class TestFactoryWithPublicAttributes:
        __slots__ = ()

        invalid_attribute = "invalid_attribute"

        def __call__(self) -> int:
            raise NotImplementedError()

    container = DictFactoryContainer()

    with pytest.raises(InvalidFactoryTypeException):
        container.set_factory(TestFactoryWithPublicAttributes, TestFactoryWithPublicAttributes())


def test_setting_non_callable_factory() -> None:
    class NoNCallableTestFactory:
        __slots__ = ()

    container = DictFactoryContainer()

    with pytest.raises(InvalidFactoryTypeException):
        container.set_factory(NoNCallableTestFactory, NoNCallableTestFactory())  # type: ignore


def test_setting_factory_with_different_type() -> None:
    class NotSubClassTestFactory:
        __slots__ = ()

        def __call__(self) -> int:
            return 42

    container = DictFactoryContainer()

    with pytest.raises(InvalidFactoryException):
        container.set_factory(SomeFactory, NotSubClassTestFactory())  # type: ignore
