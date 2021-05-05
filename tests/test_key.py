from ioc import (
    Key,
)
from util import (
    FactoryForTest,
)


def test_factory_type_property() -> None:
    key = Key(FactoryForTest)
    assert key.factory_type == FactoryForTest


def test_id_property() -> None:
    key = Key(FactoryForTest, "1")
    assert key.id == "1"


def test_eq() -> None:
    class AnotherFactoryForTest:
        def __call__(self) -> int:
            raise NotImplementedError()

    key1 = Key(FactoryForTest, "1")
    key2 = Key(FactoryForTest, "1")
    key3 = Key(FactoryForTest, "2")
    key4 = Key(AnotherFactoryForTest, "1")

    assert key1 == key2
    assert key1 != key3
    assert key1 != key4


def test_hash() -> None:
    key1 = Key(FactoryForTest, "1")
    key2 = Key(FactoryForTest, "1")

    assert hash(key1) == hash(key2)
