from congratulations_app.messengers import Messenger, MessengerFactory
from galo_ioc import add_factory

__all__ = [
    "TelegramMessenger",
    "load",
]


class TelegramMessenger(Messenger):
    def send_message(self, name: str, message: str) -> None:
        print(f"Message {message!r} sent to {name!r} via Telegram.")


def load() -> None:
    class TelegramMessengerFactory(MessengerFactory):
        def __call__(self) -> Messenger:
            return messenger

    messenger = TelegramMessenger()
    add_factory(MessengerFactory, TelegramMessengerFactory())
