import pytest
from ioc import (
    Key,
)


class SomeFactory:
    __slots__ = ()

    def __call__(self) -> int:
        raise NotImplementedError()


def test_factory_type_property() -> None:
    key = Key(SomeFactory)
    assert key.factory_type == SomeFactory


def test_id_property() -> None:
    key = Key(SomeFactory, "1")
    assert key.id == "1"


def test_eq() -> None:
    class SomeAnotherFactory:
        __slots__ = ()

        def __call__(self) -> int:
            raise NotImplementedError()

    key1 = Key(SomeFactory, "1")
    key2 = Key(SomeFactory, "1")
    key3 = Key(SomeFactory, "2")
    key4 = Key(SomeAnotherFactory, "1")

    assert key1 == key2
    assert key1 != key3
    assert key1 != key4


def test_hash() -> None:
    key1 = Key(SomeFactory, "1")
    key2 = Key(SomeFactory, "1")

    assert hash(key1) == hash(key2)
