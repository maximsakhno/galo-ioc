from typing import (
    TypeVar,
    Optional,
    Any,
    Tuple,
    Dict,
    Type,
)
from inspect import (
    Signature,
)
from ..core import (
    FactoryNotFoundException,
    FactoryContainer,
)
from ..util import (
    check_factory_type,
    get_signature,
)


__all__ = [
    "DictFactoryContainer",
]


F = TypeVar("F")


class DictFactoryContainer(FactoryContainer):
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[Tuple[Signature, Optional[Any]], Any] = {}

    def get_factory(self, factory_type: Type[F], key: Optional[Any] = None) -> F:
        check_factory_type(factory_type)
        signature = get_signature(factory_type)
        try:
            return self.__factories[(signature, key)]
        except KeyError:
            raise FactoryNotFoundException(factory_type, key) from None

    def set_factory(self, factory_type: Type[F], factory: F, key: Optional[Any] = None) -> None:
        check_factory_type(factory_type)
        signature = get_signature(factory_type)
        self.__factories[(signature, key)] = factory
