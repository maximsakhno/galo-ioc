from typing import (
    TypeVar,
    Optional,
    Callable,
    Any,
    Tuple,
    Dict,
    Type,
)
from ..util import (
    check_factory_type,
)
from ..core import (
    InvalidFactoryException,
    FactoryNotFoundException,
    FactoryContainer,
)


__all__ = [
    "DictFactoryContainer",
]


F = TypeVar("F", bound=Callable)


class DictFactoryContainer(FactoryContainer):
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[Tuple[Type[Any], Optional[Any]], Any] = {}

    def get_factory(self, factory_type: Type[F], id: Optional[Any] = None) -> F:
        check_factory_type(factory_type)
        try:
            return self.__factories[(factory_type, id)]
        except KeyError:
            raise FactoryNotFoundException(factory_type, id) from None

    def set_factory(self, factory_type: Type[F], factory: F, id: Optional[Any] = None) -> None:
        check_factory_type(factory_type)
        if not isinstance(factory, factory_type):
            raise InvalidFactoryException(factory, f"Must be instance of '{factory_type}'") from None
        self.__factories[(factory_type, id)] = factory
