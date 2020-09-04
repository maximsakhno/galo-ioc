import pytest
from ioc import (
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


def test_getitem() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    with pytest.raises(KeyError):
        nested[Key(SomeFactory)]
    parent[Key(SomeFactory)] = SomeFactoryStub(42)
    assert nested[Key(SomeFactory)]() == 42
    nested[Key(SomeFactory)] = SomeFactoryStub(43)
    assert nested[Key(SomeFactory)]() == 43
    assert parent[Key(SomeFactory)]() == 42


def test_delitem() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    parent[Key(SomeFactory)] = SomeFactoryStub(42)
    nested[Key(SomeFactory)] = SomeFactoryStub(42)
    del nested[Key(SomeFactory)]
    assert Key(SomeFactory) in parent
    del nested[Key(SomeFactory)]
    assert Key(SomeFactory) in parent


def test_contains() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert Key(SomeFactory) not in nested
    parent[Key(SomeFactory)] = SomeFactoryStub(42)
    assert Key(SomeFactory) in nested
    nested[Key(SomeFactory)] = SomeFactoryStub(42)
    assert Key(SomeFactory) in nested
    del parent[Key(SomeFactory)]
    assert Key(SomeFactory) in nested


def test_iter() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert set(nested) == set()
    parent[Key(SomeFactory, "1")] = SomeFactoryStub(42)
    assert set(nested) == {Key(SomeFactory, "1")}
    nested[Key(SomeFactory, "1")] = SomeFactoryStub(42)
    assert set(nested) == {Key(SomeFactory, "1")}
    nested[Key(SomeFactory, "2")] = SomeFactoryStub(42)
    assert set(nested) == {Key(SomeFactory, "1"), Key(SomeFactory, "2")}


def test_len() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert len(nested) == 0
    parent[Key(SomeFactory, "1")] = SomeFactoryStub(42)
    assert len(nested) == 1
    nested[Key(SomeFactory, "1")] = SomeFactoryStub(42)
    assert len(nested) == 1
    nested[Key(SomeFactory, "2")] = SomeFactoryStub(42)
    assert len(nested) == 2


def test_bool() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert not nested
    parent[Key(SomeFactory)] = SomeFactoryStub(42)
    assert nested
    nested[Key(SomeFactory)] = SomeFactoryStub(42)
    assert nested
    del parent[Key(SomeFactory)]
    assert nested
