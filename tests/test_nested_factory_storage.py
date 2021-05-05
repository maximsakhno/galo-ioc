from unittest.mock import (
    Mock,
)
from pytest import (
    fixture,
    raises,
)
from ioc import (
    Key,
    DictFactoryStorage,
    NestedFactoryStorage,
)
from util import (
    FactoryForTest,
)


@fixture
def parent() -> DictFactoryStorage:
    return DictFactoryStorage()


@fixture
def nested(parent: DictFactoryStorage) -> NestedFactoryStorage:
    return NestedFactoryStorage(DictFactoryStorage(), parent)


def test_getitem(parent: DictFactoryStorage, nested: NestedFactoryStorage) -> None:
    with raises(KeyError):
        nested[Key(FactoryForTest)]
        
    factory_for_test1 = Mock(FactoryForTest)
    factory_for_test2 = Mock(FactoryForTest)
    
    parent[Key(FactoryForTest)] = factory_for_test1
    assert nested[Key(FactoryForTest)] is factory_for_test1
    
    nested[Key(FactoryForTest)] = factory_for_test2
    assert parent[Key(FactoryForTest)] is factory_for_test1
    assert nested[Key(FactoryForTest)] is factory_for_test2


def test_delitem(parent: DictFactoryStorage, nested: NestedFactoryStorage) -> None:
    parent[Key(FactoryForTest)] = Mock(FactoryForTest)
    nested[Key(FactoryForTest)] = Mock(FactoryForTest)
    
    del nested[Key(FactoryForTest)]
    assert Key(FactoryForTest) in parent
    
    del nested[Key(FactoryForTest)]
    assert Key(FactoryForTest) in parent


def test_contains(parent: DictFactoryStorage, nested: NestedFactoryStorage) -> None:
    assert Key(FactoryForTest) not in nested
    
    parent[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert Key(FactoryForTest) in nested
    
    nested[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert Key(FactoryForTest) in nested
    
    del parent[Key(FactoryForTest)]
    assert Key(FactoryForTest) in nested


def test_iter(parent: DictFactoryStorage, nested: NestedFactoryStorage) -> None:
    assert set(nested) == set()
    
    parent[Key(FactoryForTest, "a")] = Mock(FactoryForTest)
    assert set(nested) == {Key(FactoryForTest, "a")}
    
    nested[Key(FactoryForTest, "a")] = Mock(FactoryForTest)
    assert set(nested) == {Key(FactoryForTest, "a")}
    
    nested[Key(FactoryForTest, "b")] = Mock(FactoryForTest)
    assert set(nested) == {Key(FactoryForTest, "a"), Key(FactoryForTest, "b")}


def test_len(parent: DictFactoryStorage, nested: NestedFactoryStorage) -> None:
    assert len(nested) == 0

    parent[Key(FactoryForTest, "a")] = Mock(FactoryForTest)
    assert len(nested) == 1

    nested[Key(FactoryForTest, "a")] = Mock(FactoryForTest)
    assert len(nested) == 1

    nested[Key(FactoryForTest, "b")] = Mock(FactoryForTest)
    assert len(nested) == 2


def test_bool(parent: DictFactoryStorage, nested: NestedFactoryStorage) -> None:
    assert not nested

    parent[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert nested

    nested[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert nested

    del parent[Key(FactoryForTest)]
    assert nested
