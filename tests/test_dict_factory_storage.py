import pytest
from ioc import (
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


def test_getitem() -> None:
    storage = DictFactoryStorage()
    with pytest.raises(KeyError):
        storage[Key(SomeFactory)]
    storage[Key(SomeFactory)] = SomeFactoryStub(42)
    assert storage[Key(SomeFactory)]() == 42


def test_contains() -> None:
    storage = DictFactoryStorage()
    storage[Key(SomeFactory)] = SomeFactoryStub(42)
    assert Key(SomeFactory) in storage
    del storage[Key(SomeFactory)]
    assert Key(SomeFactory) not in storage


def test_len() -> None:
    storage = DictFactoryStorage()
    assert len(storage) == 0
    storage[Key(SomeFactory)] = SomeFactoryStub(42)
    assert len(storage) == 1
    storage[Key(SomeFactory)] = SomeFactoryStub(43)
    assert len(storage) == 1


def test_iter() -> None:
    storage = DictFactoryStorage()
    assert set(storage) == set()
    storage[Key(SomeFactory)] = SomeFactoryStub(42)
    assert set(storage) == {Key(SomeFactory)}


def test_bool() -> None:
    storage = DictFactoryStorage()
    assert not storage
    storage[Key(SomeFactory)] = SomeFactoryStub(42)
    assert storage


def test_setitem_using_factory_with_public_attributes() -> None:
    class SomeFactoryWithPublicAttributes:
        __slots__ = ()

        public_attribute = "public_attribute"

        def __call__(self) -> int:
            raise NotImplementedError()

    storage = DictFactoryStorage()
    with pytest.raises(TypeError):
        storage[Key(SomeFactoryWithPublicAttributes)] = SomeFactoryWithPublicAttributes()


def test_setitem_using_non_callable_factory() -> None:
    class NoNCallableFactory:
        __slots__ = ()

    storage = DictFactoryStorage()
    with pytest.raises(TypeError):
        storage[Key(NoNCallableFactory)] = NoNCallableFactory()  # type: ignore


def test_setitem_using_factory_with_different_type() -> None:
    class NotSubClassTestFactory:
        __slots__ = ()

        def __call__(self) -> int:
            return 42

    storage = DictFactoryStorage()
    with pytest.raises(TypeError):
        storage[Key(SomeFactory)] = NotSubClassTestFactory()  # type: ignore
