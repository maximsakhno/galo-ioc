import pytest
from ioc import (
    FactoryNotFoundException,
    Key,
    DictFactoryStorage,
    NestedFactoryStorage,
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
    parent_storage = DictFactoryStorage()
    nested_storage = NestedFactoryStorage(DictFactoryStorage(), parent_storage)
    assert set(parent_storage.keys) == set()
    assert set(nested_storage.keys) == set()

    parent_storage.set_factory(Key(SomeFactory), SomeFactoryStub(42))
    assert set(parent_storage.keys) == {Key(SomeFactory)}
    assert set(nested_storage.keys) == {Key(SomeFactory)}

    nested_storage.set_factory(Key(SomeFactory, "1"), SomeFactoryStub(1))
    assert set(parent_storage.keys) == {Key(SomeFactory)}
    assert set(nested_storage.keys) == {Key(SomeFactory), Key(SomeFactory, "1")}


def test_getting_factory_in_parent_storage_from_nested_storage() -> None:
    parent_storage = DictFactoryStorage()
    nested_storage = NestedFactoryStorage(DictFactoryStorage(), parent_storage)
    parent_storage.set_factory(Key(SomeFactory), SomeFactoryStub(42))
    assert nested_storage.get_factory(Key(SomeFactory))() == 42


def test_getting_missing_factory() -> None:
    parent_storage = DictFactoryStorage()
    nested_storage = NestedFactoryStorage(DictFactoryStorage(), parent_storage)

    with pytest.raises(FactoryNotFoundException):
        nested_storage.get_factory(Key(SomeFactory))


def test_setting_factory_to_nested_storage() -> None:
    parent_storage = DictFactoryStorage()
    nested_storage = NestedFactoryStorage(DictFactoryStorage(), parent_storage)
    nested_storage.set_factory(Key(SomeFactory), SomeFactoryStub(42))
    assert nested_storage.get_factory(Key(SomeFactory))() == 42

    with pytest.raises(FactoryNotFoundException):
        parent_storage.get_factory(Key(SomeFactory))
