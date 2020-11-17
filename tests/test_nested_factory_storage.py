from pytest import (
    raises,
)
from ioc import (
    Key,
    DictFactoryStorage,
    NestedFactoryStorage,
)


class TestFactory:
    def __call__(self) -> int:
        raise NotImplementedError()


class TestFactoryImpl(TestFactory):
    def __init__(self, value: int) -> None:
        self.__value = value

    def __call__(self) -> int:
        return self.__value


def test_getitem() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    with raises(KeyError):
        nested[Key(TestFactory)]
    parent[Key(TestFactory)] = TestFactoryImpl(42)
    assert nested[Key(TestFactory)]() == 42
    nested[Key(TestFactory)] = TestFactoryImpl(43)
    assert nested[Key(TestFactory)]() == 43
    assert parent[Key(TestFactory)]() == 42


def test_delitem() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    parent[Key(TestFactory)] = TestFactoryImpl(42)
    nested[Key(TestFactory)] = TestFactoryImpl(42)
    del nested[Key(TestFactory)]
    assert Key(TestFactory) in parent
    del nested[Key(TestFactory)]
    assert Key(TestFactory) in parent


def test_contains() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert Key(TestFactory) not in nested
    parent[Key(TestFactory)] = TestFactoryImpl(42)
    assert Key(TestFactory) in nested
    nested[Key(TestFactory)] = TestFactoryImpl(42)
    assert Key(TestFactory) in nested
    del parent[Key(TestFactory)]
    assert Key(TestFactory) in nested


def test_iter() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert set(nested) == set()
    parent[Key(TestFactory, "1")] = TestFactoryImpl(42)
    assert set(nested) == {Key(TestFactory, "1")}
    nested[Key(TestFactory, "1")] = TestFactoryImpl(42)
    assert set(nested) == {Key(TestFactory, "1")}
    nested[Key(TestFactory, "2")] = TestFactoryImpl(42)
    assert set(nested) == {Key(TestFactory, "1"), Key(TestFactory, "2")}


def test_len() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert len(nested) == 0
    parent[Key(TestFactory, "1")] = TestFactoryImpl(42)
    assert len(nested) == 1
    nested[Key(TestFactory, "1")] = TestFactoryImpl(42)
    assert len(nested) == 1
    nested[Key(TestFactory, "2")] = TestFactoryImpl(42)
    assert len(nested) == 2


def test_bool() -> None:
    parent = DictFactoryStorage()
    nested = NestedFactoryStorage(DictFactoryStorage(), parent)
    assert not nested
    parent[Key(TestFactory)] = TestFactoryImpl(42)
    assert nested
    nested[Key(TestFactory)] = TestFactoryImpl(42)
    assert nested
    del parent[Key(TestFactory)]
    assert nested
