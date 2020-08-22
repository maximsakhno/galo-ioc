import pytest
from ioc import (
    InvalidFactoryTypeException,
    InvalidFactoryException,
    FactoryNotFoundException,
    Key,
    DictFactoryStorage,
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


def test_keys() -> None:
    storage = DictFactoryStorage()
    assert set(storage.keys) == set()

    storage.set_factory(Key(SomeFactory), SomeFactoryStub(42))
    assert set(storage.keys) == {Key(SomeFactory)}

    storage.set_factory(Key(SomeFactory, "1"), SomeFactoryStub(1))
    storage.set_factory(Key(SomeFactory, "1"), SomeFactoryStub(1))
    assert set(storage.keys) == {Key(SomeFactory), Key(SomeFactory, "1")}


def test_getting_existing_factory() -> None:
    storage = DictFactoryStorage()
    storage.set_factory(Key(SomeFactory), SomeFactoryStub(42))
    assert storage.get_factory(Key(SomeFactory))() == 42


def test_getting_missing_factory() -> None:
    storage = DictFactoryStorage()

    with pytest.raises(FactoryNotFoundException):
        storage.get_factory(Key(SomeFactory))


def test_getting_factory_by_id() -> None:
    storage = DictFactoryStorage()
    storage.set_factory(Key(SomeFactory, "1"), SomeFactoryStub(42))

    with pytest.raises(FactoryNotFoundException):
        storage.get_factory(Key(SomeFactory))

    with pytest.raises(FactoryNotFoundException):
        storage.get_factory(Key(SomeFactory, "2"))

    assert storage.get_factory(Key(SomeFactory, "1"))() == 42


def test_setting_factory_invalid_attributes() -> None:
    class SomeFactoryWithPublicAttributes:
        __slots__ = ()

        public_attribute = "public_attribute"

        def __call__(self) -> int:
            raise NotImplementedError()

    storage = DictFactoryStorage()

    with pytest.raises(InvalidFactoryTypeException):
        storage.set_factory(Key(SomeFactoryWithPublicAttributes), SomeFactoryWithPublicAttributes())


def test_setting_non_callable_factory() -> None:
    class NoNCallableFactory:
        __slots__ = ()

    storage = DictFactoryStorage()

    with pytest.raises(InvalidFactoryTypeException):
        storage.set_factory(Key(NoNCallableFactory), NoNCallableFactory())  # type: ignore


def test_setting_factory_with_different_type() -> None:
    class NotSubClassTestFactory:
        __slots__ = ()

        def __call__(self) -> int:
            return 42

    storage = DictFactoryStorage()

    with pytest.raises(InvalidFactoryException):
        storage.set_factory(Key(SomeFactory), NotSubClassTestFactory())  # type: ignore
