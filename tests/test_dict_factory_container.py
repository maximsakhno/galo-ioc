import pytest
from typing import (
    Protocol,
)
from ioc import (
    InvalidFactoryTypeException,
    FactoryNotFoundException,
    DictFactoryContainer,
)


class IntegerFactory(Protocol):
    __slots__ = ()

    def __call__(self) -> int:
        raise NotImplementedError()


def test_getting_existing_factory() -> None:
    container = DictFactoryContainer()
    container.set_factory(IntegerFactory, lambda: 0)
    assert container.get_factory(IntegerFactory)() == 0


def test_getting_missing_factory() -> None:
    container = DictFactoryContainer()

    with pytest.raises(FactoryNotFoundException):
        container.get_factory(IntegerFactory)


def test_getting_factory_with_same_signature() -> None:
    class IntegerFactoryWithSameSignature(Protocol):
        __slots__ = ()

        def __call__(self) -> int:
            raise NotImplementedError()

    container = DictFactoryContainer()
    container.set_factory(IntegerFactory, lambda: 0)
    assert container.get_factory(IntegerFactoryWithSameSignature)() == 0


def test_getting_factory_by_id() -> None:
    container = DictFactoryContainer()
    container.set_factory(IntegerFactory, lambda: 0, "integer_factory")

    with pytest.raises(FactoryNotFoundException):
        container.get_factory(IntegerFactory)

    with pytest.raises(FactoryNotFoundException):
        container.get_factory(IntegerFactory, "another_integer_factory")

    assert container.get_factory(IntegerFactory, "integer_factory")() == 0


def test_setting_no_protocol_factory() -> None:
    class NoProtocolIntegerFactory:
        __slots__ = ()

        def __call__(self) -> int:
            raise NotImplementedError()

    container = DictFactoryContainer()

    with pytest.raises(InvalidFactoryTypeException):
        container.set_factory(NoProtocolIntegerFactory, lambda: 0)


def test_setting_factory_with_public_attributes() -> None:
    class IntegerFactoryWithPublicAttributes(Protocol):
        __slots__ = ()

        public_attribute = "public_attribute"

        def __call__(self) -> int:
            raise NotImplementedError()

    container = DictFactoryContainer()

    with pytest.raises(InvalidFactoryTypeException):
        container.set_factory(IntegerFactoryWithPublicAttributes, lambda: 0)


def test_setting_no_callable_factory() -> None:
    class NoCallableIntegerFactory(Protocol):
        __slots__ = ()

    class NoCallableIntegerFactoryImpl(NoCallableIntegerFactory):
        __slots__ = ()

    container = DictFactoryContainer()

    with pytest.raises(InvalidFactoryTypeException):
        container.set_factory(NoCallableIntegerFactory, NoCallableIntegerFactoryImpl())
