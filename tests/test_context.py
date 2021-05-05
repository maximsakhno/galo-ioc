from unittest.mock import (
    Mock,
    AsyncMock,
)
from pytest import (
    fixture,
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
from util import (
    FactoryForTest,
)


@fixture
def factory_storage() -> DictFactoryStorage:
    return DictFactoryStorage()


def test_get_factory_storage(factory_storage: DictFactoryStorage) -> None:
    factory_for_test = Mock(FactoryForTest)
    factory_storage[Key(FactoryForTest)] = factory_for_test

    with raises(FactoryStorageNotFoundException):
        get_factory_storage()

    with factory_storage:
        assert get_factory_storage()[Key(FactoryForTest)] is factory_for_test


def test_get_factory(factory_storage: DictFactoryStorage) -> None:
    factory_for_test = Mock(FactoryForTest, return_value=1)
    proxy_factory_for_test = get_factory(Key(FactoryForTest))

    with raises(FactoryStorageNotFoundException):
        proxy_factory_for_test()

    with factory_storage:
        with raises(KeyError):
            proxy_factory_for_test()

        factory_storage[Key(FactoryForTest)] = factory_for_test
        assert proxy_factory_for_test() == 1
        factory_for_test.assert_called_once()


def test_get_factory_getter(factory_storage: DictFactoryStorage) -> None:
    factory_for_test = Mock(FactoryForTest)
    get_factory_for_test = get_factory_getter(Key(FactoryForTest))

    with raises(FactoryStorageNotFoundException):
        get_factory_for_test()

    with factory_storage:
        with raises(KeyError):
            get_factory_for_test()

        factory_storage[Key(FactoryForTest)] = factory_for_test
        assert get_factory_for_test() is factory_for_test


def test_set_factory() -> None:
    factory_for_test = Mock(FactoryForTest, return_value=1)
    proxy_factory_for_test = get_factory(Key(FactoryForTest))

    with DictFactoryStorage():
        with raises(KeyError):
            proxy_factory_for_test()

        set_factory(Key(FactoryForTest), factory_for_test)
        assert proxy_factory_for_test() == 1
        factory_for_test.assert_called_once()


def test_get_factory_setter() -> None:
    factory_for_test = Mock(FactoryForTest)
    get_factory_for_test = get_factory_getter(Key(FactoryForTest))
    set_factory_for_test = get_factory_setter(Key(FactoryForTest))

    with raises(FactoryStorageNotFoundException):
        set_factory_for_test(factory_for_test)

    with DictFactoryStorage():
        set_factory_for_test(factory_for_test)
        assert get_factory_for_test() is factory_for_test


def test_proxy_factory_with_different_contexts() -> None:
    proxy_factory_for_test, set_factory_for_test = use_factory(Key(FactoryForTest))
    with DictFactoryStorage():
        set_factory_for_test(Mock(FactoryForTest))
    with DictFactoryStorage():
        with raises(KeyError):
            proxy_factory_for_test()


def test_proxy_factory_with_nested_contexts() -> None:
    proxy_factory_for_test, set_factory_for_test = use_factory(Key(FactoryForTest))
    with DictFactoryStorage():
        set_factory_for_test(Mock(FactoryForTest, return_value=1))
        with DictFactoryStorage():
            assert proxy_factory_for_test() == 1
            set_factory_for_test(Mock(FactoryForTest, return_value=2))
            assert proxy_factory_for_test() == 2
        assert proxy_factory_for_test() == 1


def test_entering_to_the_context_multiple_times() -> None:
    storage1 = DictFactoryStorage()
    storage2 = DictFactoryStorage()

    storage1[Key(FactoryForTest)] = Mock(FactoryForTest, return_value=1)
    storage2[Key(FactoryForTest)] = Mock(FactoryForTest, return_value=2)

    test_factory = get_factory(Key(FactoryForTest))

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
    test_factory1, set_test_factory1 = use_factory(Key(FactoryForTest, "1"))
    test_factory2, set_test_factory2 = use_factory(Key(FactoryForTest, "2"))

    with DictFactoryStorage():
        set_test_factory1(Mock(FactoryForTest, return_value=1))
        with raises(KeyError):
            test_factory2()
        set_test_factory2(Mock(FactoryForTest, return_value=2))
        assert test_factory1() == 1
        assert test_factory2() == 2


@mark.asyncio
async def test_async_proxy_factory() -> None:
    class AsyncFactoryForTest:
        async def __call__(self) -> int:
            raise NotImplementedError()

    test_factory, set_test_factory = use_factory(Key(AsyncFactoryForTest))
    with DictFactoryStorage():
        set_test_factory(AsyncMock(AsyncFactoryForTest, return_value=1))
        assert await test_factory() == 1
