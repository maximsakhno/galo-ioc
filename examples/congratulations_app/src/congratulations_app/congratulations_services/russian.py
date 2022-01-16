from congratulations_app.congratulations_services import (
    CongratulationsService,
    CongratulationsServiceFactory,
)
from congratulations_app.messengers import Messenger, MessengerFactory
from galo_ioc import add_factory, get_factory

__all__ = [
    "RussianCongratulationsService",
    "load",
]


class RussianCongratulationsService(CongratulationsService):
    def __init__(self, messenger: Messenger) -> None:
        self.__messenger = messenger

    def happy_birthday(self, name: str) -> None:
        self.__messenger.send_message(name, f"С днем рождения, {name}!")


def load() -> None:
    class RussianCongratulationsServiceFactory(CongratulationsServiceFactory):
        def __call__(self) -> CongratulationsService:
            return service

    messenger_factory = get_factory(MessengerFactory)
    messenger = messenger_factory()
    service = RussianCongratulationsService(messenger)
    add_factory(CongratulationsServiceFactory, RussianCongratulationsServiceFactory())
