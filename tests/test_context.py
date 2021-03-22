from pytest import (
    raises,
    mark,
)
from ioc import (
    FactoryStorageNotFoundException,
    Key,
    DictFactoryStorage,
    get_factory_storage,
    get_factory_getter,
    get_factory_setter,
    get_factory,
    set_factory,
    use_factory,
)


class TestFactory:
    def __call__(self) -> int:
        raise NotImplementedError()


class TestFactoryImpl(TestFactory):
    def __init__(self, value: int) -> None:
        self.__value = value

    def __call__(self) -> int:
        return self.__value


def test_get_factory_storage() -> None:
    factory_storage = DictFactoryStorage()
    factory_storage[Key(TestFactory)] = TestFactoryImpl(1)

    with raises(FactoryStorageNotFoundException):
        get_factory_storage()

    with factory_storage:
        assert get_factory_storage()[Key(TestFactory)]() == 1


def test_get_factory_getter() -> None:
    factory_storage = DictFactoryStorage()
    get_test_factory = get_factory_getter(Key(TestFactory))

    with raises(FactoryStorageNotFoundException):
        get_test_factory()

    with factory_storage:
        with raises(KeyError):
            get_test_factory()

        factory_storage[Key(TestFactory)] = TestFactoryImpl(1)
        test_factory = get_test_factory()
        assert test_factory() == 1


def test_get_factory_setter() -> None:
    test_factory = get_factory(Key(TestFactory))
    set_test_factory = get_factory_setter(Key(TestFactory))

    with raises(FactoryStorageNotFoundException):
        set_test_factory(TestFactoryImpl(1))

    with DictFactoryStorage():
        set_test_factory(TestFactoryImpl(1))
        assert test_factory() == 1


def test_get_factory() -> None:
    factory_storage = DictFactoryStorage()
    test_factory = get_factory(Key(TestFactory))

    with raises(FactoryStorageNotFoundException):
        test_factory()

    with factory_storage:
        with raises(KeyError):
            test_factory()

        factory_storage[Key(TestFactory)] = TestFactoryImpl(1)
        assert test_factory() == 1


def test_set_factory() -> None:
    test_factory = get_factory(Key(TestFactory))

    with DictFactoryStorage():
        with raises(KeyError):
            test_factory()

        set_factory(Key(TestFactory), TestFactoryImpl(1))
        assert test_factory() == 1


def test_proxy_factory_with_different_contexts() -> None:
    test_factory, set_test_factory = use_factory(Key(TestFactory))
    with DictFactoryStorage():
        set_test_factory(TestFactoryImpl(42))
    with DictFactoryStorage():
        with raises(KeyError):
            test_factory()


def test_proxy_factory_with_nested_contexts() -> None:
    test_factory, set_test_factory = use_factory(Key(TestFactory))
    with DictFactoryStorage():
        set_test_factory(TestFactoryImpl(1))
        with DictFactoryStorage():
            assert test_factory() == 1
            set_test_factory(TestFactoryImpl(2))
            assert test_factory() == 2
        assert test_factory() == 1


def test_enter_to_context_multiple_times() -> None:
    storage1 = DictFactoryStorage()
    storage2 = DictFactoryStorage()

    storage1[Key(TestFactory)] = TestFactoryImpl(1)
    storage2[Key(TestFactory)] = TestFactoryImpl(2)

    test_factory = get_factory(Key(TestFactory))

    with storage1:
        assert test_factory() == 1
        with storage1:
            assert test_factory() == 1
            with storage2:
                assert test_factory() == 2
            assert test_factory() == 1
        assert test_factory() == 1

    with storage1:
        assert test_factory() == 1
        with storage2:
            assert test_factory() == 2
            with storage1:
                assert test_factory() == 1
            assert test_factory() == 2
        assert test_factory() == 1


def test_different_proxy_factories_with_the_same_factory_type() -> None:
    test_factory1, set_test_factory1 = use_factory(Key(TestFactory, "1"))
    test_factory2, set_test_factory2 = use_factory(Key(TestFactory, "2"))

    with DictFactoryStorage():
        set_test_factory1(TestFactoryImpl(1))
        with raises(KeyError):
            test_factory2()
        set_test_factory2(TestFactoryImpl(2))
        assert test_factory1() == 1
        assert test_factory2() == 2


@mark.asyncio
async def test_async_proxy_factory() -> None:
    class AsyncTestFactory:
        async def __call__(self) -> int:
            raise NotImplementedError()

    class AsyncTestFactoryImpl(AsyncTestFactory):
        async def __call__(self) -> int:
            return 42

    test_factory, set_test_factory = use_factory(Key(AsyncTestFactory))
    with DictFactoryStorage():
        set_test_factory(AsyncTestFactoryImpl())
        assert await test_factory() == 42
