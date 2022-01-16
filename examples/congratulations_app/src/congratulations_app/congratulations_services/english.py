from congratulations_app.congratulations_services import (
    CongratulationsService,
    CongratulationsServiceFactory,
)
from congratulations_app.messengers import Messenger, MessengerFactory
from galo_ioc import add_factory, get_factory

__all__ = [
    "EnglishCongratulationsService",
    "load",
]


class EnglishCongratulationsService(CongratulationsService):
    def __init__(self, messenger: Messenger) -> None:
        self.__messenger = messenger

    def happy_birthday(self, name: str) -> None:
        self.__messenger.send_message(name, f"Happy birthday, {name}!")


def load() -> None:
    class EnglishCongratulationsServiceFactory(CongratulationsServiceFactory):
        def __call__(self) -> CongratulationsService:
            return service

    messenger_factory = get_factory(MessengerFactory)
    messenger = messenger_factory()
    service = EnglishCongratulationsService(messenger)
    add_factory(CongratulationsServiceFactory, EnglishCongratulationsServiceFactory())
