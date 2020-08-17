import pytest
from typing import (
    Protocol,
    Any,
    Tuple,
    Dict,
)
from ioc import (
    FactoryContainerNotSetException,
    FactoryNotFoundException,
    DictFactoryContainer,
    using_factory_container,
    get_factory,
    use_factory,
    get_instance,
)


class IntegerFactory(Protocol):
    __slots__ = ()

    def __call__(self) -> int:
        raise NotImplementedError()


def test_calling_proxy_factory_out_of_factory_container_context() -> None:
    integer_factory = get_factory(IntegerFactory)

    with pytest.raises(FactoryContainerNotSetException):
        integer_factory()


def test_calling_proxy_factory_inside_factory_container_context() -> None:
    integer_factory, integer_factory_setter = use_factory(IntegerFactory)

    with using_factory_container(DictFactoryContainer()):
        with pytest.raises(FactoryNotFoundException):
            integer_factory()

        integer_factory_setter(lambda: 0)
        assert integer_factory() == 0


def test_calling_proxy_factory_inside_different_factory_container_contexts() -> None:
    integer_factory, integer_factory_setter = use_factory(IntegerFactory)

    with using_factory_container(DictFactoryContainer()):
        integer_factory_setter(lambda: 0)

    with using_factory_container(DictFactoryContainer()):
        with pytest.raises(FactoryNotFoundException):
            integer_factory()


def test_nested_factory_container_context() -> None:
    integer_factory, integer_factory_setter = use_factory(IntegerFactory)

    with using_factory_container(DictFactoryContainer()):
        integer_factory_setter(lambda: 0)

        with using_factory_container(DictFactoryContainer()):
            assert integer_factory() == 0

            integer_factory_setter(lambda: 1)
            assert integer_factory() == 1

        assert integer_factory() == 0


def test_different_proxy_factories_with_the_same_factory_type() -> None:
    integer_factory1, integer_factory_setter1 = use_factory(IntegerFactory)
    integer_factory2, integer_factory_setter2 = use_factory(IntegerFactory)

    with using_factory_container(DictFactoryContainer()):
        integer_factory_setter1(lambda: 0)

        with pytest.raises(FactoryNotFoundException):
            integer_factory2()

        integer_factory_setter2(lambda: 1)

        assert integer_factory1() == 0
        assert integer_factory2() == 1


def test_accessing_to_proxy_instance() -> None:
    class Dependency:
        __slots__ = ()

        def some_method(self) -> int:
            raise NotImplementedError()

    class DependencyImpl(Dependency):
        __slots__ = ()

        def some_method(self) -> int:
            return 42

    class DependencyFactory(Protocol):
        __slots__ = ()

        def __call__(self) -> Dependency:
            raise NotImplementedError()

    dependency_factory, dependency_factory_setter = use_factory(DependencyFactory)
    dependency = get_instance(Dependency, dependency_factory)

    with pytest.raises(FactoryContainerNotSetException):
        dependency.some_method()

    with using_factory_container(DictFactoryContainer()):
        with pytest.raises(FactoryNotFoundException):
            dependency.some_method()

        dependency_factory_setter(lambda: DependencyImpl())
        assert dependency.some_method() == 42
