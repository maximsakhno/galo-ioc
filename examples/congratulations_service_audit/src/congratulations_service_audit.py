from logging import Logger
from typing import Dict, Optional

from congratulations_app.congratulations_services import (
    CongratulationsService,
    CongratulationsServiceFactory,
)
from galo_ioc import Factory, FactoryType, add_factory_decorator, get_factory
from loggers import LoggerFactory

__all__ = [
    "load",
]


class CongratulationsServiceWrapper(CongratulationsService):
    def __init__(self, wrappee: CongratulationsService, logger: Logger) -> None:
        self.__wrappee = wrappee
        self.__logger = logger

    def happy_birthday(self, name: str) -> None:
        self.__logger.debug(f"name={name!r}")
        return self.__wrappee.happy_birthday(name)


def load() -> None:
    def factory_decorator(
        factory_type: FactoryType,
        id: Optional[str],
        factory: Factory,
    ) -> Factory:
        if not issubclass(factory_type, CongratulationsServiceFactory):
            return factory

        class CongratulationsServiceFactoryWrapper(CongratulationsServiceFactory):
            def __call__(self) -> CongratulationsService:
                wrappee = factory()
                try:
                    return wrappers[wrappee]
                except KeyError:
                    wrappers[wrappee] = CongratulationsServiceWrapper(wrappee, logger)
                    return wrappers[wrappee]

        wrappers: Dict[CongratulationsService, CongratulationsServiceWrapper] = {}
        return CongratulationsServiceFactoryWrapper()

    logger_factory = get_factory(LoggerFactory)
    logger = logger_factory("congratulations_service_audit")
    add_factory_decorator(factory_decorator)
