from pytest import (
    raises,
)
from ioc import (
    Key,
    DictFactoryStorage,
)


class TestFactory:
    def __call__(self) -> int:
        raise NotImplementedError()


class TestFactoryStub(TestFactory):
    def __init__(self, value: int) -> None:
        self.__value = value

    def __call__(self) -> int:
        return self.__value


def test_getitem() -> None:
    storage = DictFactoryStorage()
    with raises(KeyError):
        storage[Key(TestFactory)]
    storage[Key(TestFactory)] = TestFactoryStub(42)
    assert storage[Key(TestFactory)]() == 42


def test_contains() -> None:
    storage = DictFactoryStorage()
    storage[Key(TestFactory)] = TestFactoryStub(42)
    assert Key(TestFactory) in storage
    del storage[Key(TestFactory)]
    assert Key(TestFactory) not in storage


def test_len() -> None:
    storage = DictFactoryStorage()
    assert len(storage) == 0
    storage[Key(TestFactory)] = TestFactoryStub(42)
    assert len(storage) == 1
    storage[Key(TestFactory)] = TestFactoryStub(43)
    assert len(storage) == 1


def test_iter() -> None:
    storage = DictFactoryStorage()
    assert set(storage) == set()
    storage[Key(TestFactory)] = TestFactoryStub(42)
    assert set(storage) == {Key(TestFactory)}


def test_bool() -> None:
    storage = DictFactoryStorage()
    assert not storage
    storage[Key(TestFactory)] = TestFactoryStub(42)
    assert storage


def test_setitem_using_factory_with_public_attributes() -> None:
    class SomeFactoryWithPublicAttributes:
        public_attribute = "public_attribute"

        def __call__(self) -> int:
            raise NotImplementedError()

    storage = DictFactoryStorage()
    with raises(TypeError):
        storage[Key(SomeFactoryWithPublicAttributes)] = SomeFactoryWithPublicAttributes()


def test_setitem_using_non_callable_factory() -> None:
    class NoNCallableFactory:
        pass

    storage = DictFactoryStorage()
    with raises(TypeError):
        storage[Key(NoNCallableFactory)] = NoNCallableFactory()


def test_setitem_using_factory_with_different_type() -> None:
    class NotSubClassTestFactory:
        def __call__(self) -> int:
            return 42

    storage = DictFactoryStorage()
    with raises(TypeError):
        storage[Key(TestFactory)] = NotSubClassTestFactory()
