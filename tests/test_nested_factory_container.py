import pytest
from typing import (
    Protocol,
)
from ioc import (
    InvalidFactoryTypeException,
    FactoryNotFoundException,
    DictFactoryContainer,
    NestedFactoryContainer,
)


class IntegerFactory(Protocol):
    __slots__ = ()

    def __call__(self) -> int:
        raise NotImplementedError()


def test_getting_factory_in_parent_container_from_nested_container() -> None:
    parent_container = DictFactoryContainer()
    nested_container = NestedFactoryContainer(DictFactoryContainer(), parent_container)
    parent_container.set_factory(IntegerFactory, lambda: 0)
    assert nested_container.get_factory(IntegerFactory)() == 0


def test_getting_missing_factory() -> None:
    parent_container = DictFactoryContainer()
    nested_container = NestedFactoryContainer(DictFactoryContainer(), parent_container)

    with pytest.raises(FactoryNotFoundException):
        nested_container.get_factory(IntegerFactory)


def test_setting_factory_to_nested_container() -> None:
    parent_container = DictFactoryContainer()
    nested_container = NestedFactoryContainer(DictFactoryContainer(), parent_container)
    nested_container.set_factory(IntegerFactory, lambda: 0)
    assert nested_container.get_factory(IntegerFactory)() == 0

    with pytest.raises(FactoryNotFoundException):
        parent_container.get_factory(IntegerFactory)
