from typing import Optional, Any, Type, List, Dict, NamedTuple
from ioc import Args, KwArgs, Factory, FactoryType, T, check_factory_type
from ioc.factory_containers import FactoryAlreadyAddedException, FactoryNotFoundException, FactoryDecorator
from ioc.context import FactoryContainerContextManager


__all__ = [
    "FactoryContainerImpl",
]


class FactoryKey(NamedTuple):
    factory_type: FactoryType
    id: Optional[str]


class FactoryContainerImpl(FactoryContainerContextManager):
    def __init__(self) -> None:
        super().__init__()
        self.__factories: Dict[FactoryKey, Factory] = {}
        self.__factory_decorators: List[FactoryDecorator] = []

    def add_factory(self, factory_type: Type[T], factory: T, id: Optional[str] = None) -> None:
        factory_key = FactoryKey(factory_type, id)
        try:
            factory = self.__factories[factory_key]
        except KeyError:
            check_factory_type(factory_type)
            for factory_decorator in self.__factory_decorators:
                factory = factory_decorator(factory_type, id, factory)
            self.__factories[factory_key] = factory
        else:
            raise FactoryAlreadyAddedException(factory_type, id)

    def add_factory_decorator(self, factory_decorator: FactoryDecorator) -> None:
        for factory_key in self.__factories.keys():
            factory_type, id = factory_key
            self.__factories[factory_key] = factory_decorator(factory_type, id, self.__factories[factory_key])
        self.__factory_decorators.append(factory_decorator)

    def call_factory(self, factory_type: FactoryType, id: Optional[str], args: Args, kwargs: KwArgs) -> Any:
        factory_key = FactoryKey(factory_type, id)
        try:
            factory = self.__factories[factory_key]
        except KeyError:
            raise FactoryNotFoundException(factory_type, id) from None
        return factory(*args, **kwargs)
