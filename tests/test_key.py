from ioc import (
    Key,
)


class TestFactory:
    def __call__(self) -> int:
        raise NotImplementedError()


def test_factory_type_property() -> None:
    key = Key(TestFactory)
    assert key.factory_type == TestFactory


def test_id_property() -> None:
    key = Key(TestFactory, "1")
    assert key.id == "1"


def test_eq() -> None:
    class AnotherTestFactory:
        def __call__(self) -> int:
            raise NotImplementedError()

    key1 = Key(TestFactory, "1")
    key2 = Key(TestFactory, "1")
    key3 = Key(TestFactory, "2")
    key4 = Key(AnotherTestFactory, "1")

    assert key1 == key2
    assert key1 != key3
    assert key1 != key4


def test_hash() -> None:
    key1 = Key(TestFactory, "1")
    key2 = Key(TestFactory, "1")

    assert hash(key1) == hash(key2)
