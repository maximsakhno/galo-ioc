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
)
from util import (
    FactoryForTest,
)


@fixture
def factory_storage() -> DictFactoryStorage:
    return DictFactoryStorage()


def test_getitem(factory_storage: DictFactoryStorage) -> None:
    factory_for_test = Mock(FactoryForTest)
    factory_storage[Key(FactoryForTest)] = factory_for_test
    assert factory_storage[Key(FactoryForTest)] is factory_for_test


def test_getitem_with_base_factory_type(factory_storage: DictFactoryStorage) -> None:
    class DerivedFactoryForTest(FactoryForTest):
        pass

    factory_for_test = Mock(DerivedFactoryForTest)
    factory_storage[Key(DerivedFactoryForTest)] = factory_for_test
    assert factory_storage[Key(FactoryForTest)] is factory_for_test


def test_factory_not_found(factory_storage: DictFactoryStorage) -> None:
    with raises(KeyError):
        factory_storage[Key(FactoryForTest)]


def test_delitem(factory_storage: DictFactoryStorage) -> None:
    factory_storage[Key(FactoryForTest)] = Mock(FactoryForTest)
    del factory_storage[Key(FactoryForTest)]
    with raises(KeyError):
        factory_storage[Key(FactoryForTest)]


def test_contains(factory_storage: DictFactoryStorage) -> None:
    factory_storage[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert Key(FactoryForTest) in factory_storage
    del factory_storage[Key(FactoryForTest)]
    assert Key(FactoryForTest) not in factory_storage


def test_len(factory_storage: DictFactoryStorage) -> None:
    assert len(factory_storage) == 0
    factory_storage[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert len(factory_storage) == 1


def test_iter(factory_storage: DictFactoryStorage) -> None:
    factory_storage[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert set(factory_storage) == {Key(FactoryForTest)}


def test_bool(factory_storage: DictFactoryStorage) -> None:
    assert not factory_storage
    factory_storage[Key(FactoryForTest)] = Mock(FactoryForTest)
    assert factory_storage


def test_non_callable_factory_type(factory_storage: DictFactoryStorage) -> None:
    class NonCallableFactory:
        pass

    with raises(TypeError):
        factory_storage[Key(NonCallableFactory)] = Mock(NonCallableFactory)


def test_factory_with_illegal_attribute(factory_storage: DictFactoryStorage) -> None:
    class FactoryWithIllegalAttribute:
        illegal_attribute = "illegal_attribute"

        def __call__(self) -> None:
            raise NotImplementedError()

    with raises(TypeError):
        factory_storage[Key(FactoryWithIllegalAttribute)] = Mock(FactoryWithIllegalAttribute)


def test_setitem_with_different_factory_type(factory_storage: DictFactoryStorage) -> None:
    with raises(TypeError):
        factory_storage[Key(FactoryForTest)] = Mock()
