import pytest
from ioc import (
    FactoryStorageSetException,
    FactoryStorageNotSetException,
    Key,
    DictFactoryStorage,
    get_factory,
    use_factory,
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


def test_calling_factory_proxy_out_of_factory_storage_context() -> None:
    test_factory = get_factory(Key(SomeFactory))
    with pytest.raises(FactoryStorageNotSetException):
        test_factory()


def test_calling_factory_proxy_inside_factory_storage_context() -> None:
    test_factory, set_test_factory = use_factory(Key(SomeFactory))
    with DictFactoryStorage():
        with pytest.raises(KeyError):
            test_factory()
        set_test_factory(SomeFactoryStub(42))
        assert test_factory() == 42


def test_entering_to_the_context_twice() -> None:
    storage = DictFactoryStorage()
    with storage:
        with pytest.raises(FactoryStorageSetException):
            with storage:
                pass


def test_calling_factory_proxy_inside_different_factory_storage_contexts() -> None:
    test_factory, set_test_factory = use_factory(Key(SomeFactory))
    with DictFactoryStorage():
        set_test_factory(SomeFactoryStub(42))
    with DictFactoryStorage():
        with pytest.raises(KeyError):
            test_factory()


def test_nested_factory_storage_context() -> None:
    test_factory, set_test_factory = use_factory(Key(SomeFactory))
    with DictFactoryStorage():
        set_test_factory(SomeFactoryStub(1))
        with DictFactoryStorage():
            assert test_factory() == 1
            set_test_factory(SomeFactoryStub(2))
            assert test_factory() == 2
        assert test_factory() == 1


def test_different_factory_proxies_with_the_same_factory_type() -> None:
    test_factory1, set_test_factory1 = use_factory(Key(SomeFactory, "1"))
    test_factory2, set_test_factory2 = use_factory(Key(SomeFactory, "2"))
    with DictFactoryStorage():
        set_test_factory1(SomeFactoryStub(1))
        with pytest.raises(KeyError):
            test_factory2()
        set_test_factory2(SomeFactoryStub(2))
        assert test_factory1() == 1
        assert test_factory2() == 2


def test_factory_with_different_argument_kinds_proxy() -> None:
    class SomeFactoryWithDifferentArgumentKinds:
        __slots__ = ()

        def __call__(self, a: int, /, b: int, *, c: int = 3) -> int:
            raise NotImplementedError()

    class SomeFactoryWithDifferentArgumentKindsStub(SomeFactoryWithDifferentArgumentKinds):
        __slots__ = ()

        def __call__(self, a: int, /, b: int, *, c: int = 3) -> int:
            return 42

    test_factory, set_test_factory = use_factory(Key(SomeFactoryWithDifferentArgumentKinds))
    with DictFactoryStorage():
        set_test_factory(SomeFactoryWithDifferentArgumentKindsStub())
        assert test_factory(1, 2) == 42


def test_factory_with_variadic_arguments_proxy() -> None:
    class SomeFactoryWithVariadicArguments:
        __slots__ = ()

        def __call__(self, *args: int, **kwargs: int) -> int:
            raise NotImplementedError()

    class SomeFactoryWithVariadicArgumentsStub(SomeFactoryWithVariadicArguments):
        __slots__ = ()

        def __call__(self, *args: int, **kwargs: int) -> int:
            return 42

    test_factory, set_test_factory = use_factory(Key(SomeFactoryWithVariadicArguments))
    with DictFactoryStorage():
        set_test_factory(SomeFactoryWithVariadicArgumentsStub())
        assert test_factory(1, b=2) == 42


def test_factory_with_positional_only_arguments_proxy() -> None:
    class SomeFactoryWithPositionalOnlyArguments:
        __slots__ = ()

        def __call__(self, a: int, /) -> int:
            raise NotImplementedError()

    class SomeFactoryWithPositionalOnlyArgumentsStub(SomeFactoryWithPositionalOnlyArguments):
        __slots__ = ()

        def __call__(self, a: int, /) -> int:
            return 42

    test_factory, set_test_factory = use_factory(Key(SomeFactoryWithPositionalOnlyArguments))
    with DictFactoryStorage():
        set_test_factory(SomeFactoryWithPositionalOnlyArgumentsStub())
        assert test_factory(1) == 42


@pytest.mark.asyncio
async def test_async_factory_proxy() -> None:
    class SomeAsyncFactory:
        __slots__ = ()

        async def __call__(self) -> int:
            raise NotImplementedError()

    class SomeAsyncFactoryStub(SomeAsyncFactory):
        __slots__ = ()

        async def __call__(self) -> int:
            return 42

    test_factory, set_test_factory = use_factory(Key(SomeAsyncFactory))
    with DictFactoryStorage():
        set_test_factory(SomeAsyncFactoryStub())
        assert await test_factory() == 42
