from typing import (
    TypeVar,
    Optional,
    Any,
    Type,
)
from ..core import (
    FactoryNotFoundException,
    FactoryContainer,
)


__all__ = [
    "NestedFactoryContainer",
]


F = TypeVar("F")


class NestedFactoryContainer(FactoryContainer):
    __slots__ = (
        "__factory_container",
        "__parent_factory_container",
    )

    def __init__(
        self,
        factory_container: FactoryContainer,
        parent_factory_container: FactoryContainer,
    ) -> None:
        self.__factory_container = factory_container
        self.__parent_factory_container = parent_factory_container

    def get_factory(self, factory_type: Type[F], id: Optional[Any] = None) -> F:
        try:
            return self.__factory_container.get_factory(factory_type, id)
        except FactoryNotFoundException:
            return self.__parent_factory_container.get_factory(factory_type, id)

    def set_factory(self, factory_type: Type[F], factory: F, id: Optional[Any] = None) -> None:
        self.__factory_container.set_factory(factory_type, factory, id)
