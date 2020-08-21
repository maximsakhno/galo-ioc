import pytest
from ioc import (
    FactoryNotFoundException,
    DictFactoryContainer,
    NestedFactoryContainer,
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


def test_getting_factory_in_parent_container_from_nested_container() -> None:
    parent_container = DictFactoryContainer()
    nested_container = NestedFactoryContainer(DictFactoryContainer(), parent_container)
    parent_container.set_factory(SomeFactory, SomeFactoryStub(42))
    assert nested_container.get_factory(SomeFactory)() == 42


def test_getting_missing_factory() -> None:
    parent_container = DictFactoryContainer()
    nested_container = NestedFactoryContainer(DictFactoryContainer(), parent_container)

    with pytest.raises(FactoryNotFoundException):
        nested_container.get_factory(SomeFactory)


def test_setting_factory_to_nested_container() -> None:
    parent_container = DictFactoryContainer()
    nested_container = NestedFactoryContainer(DictFactoryContainer(), parent_container)
    nested_container.set_factory(SomeFactory, SomeFactoryStub(42))
    assert nested_container.get_factory(SomeFactory)() == 42

    with pytest.raises(FactoryNotFoundException):
        parent_container.get_factory(SomeFactory)
