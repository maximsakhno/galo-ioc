from congratulations_app.messengers import Messenger, MessengerFactory
from galo_ioc import add_factory

__all__ = [
    "WhatsAppMessenger",
    "load",
]


class WhatsAppMessenger(Messenger):
    def send_message(self, name: str, message: str) -> None:
        print(f"Message {message!r} sent to {name!r} via WhatsApp.")


def load() -> None:
    class WhatsAppMessengerFactory(MessengerFactory):
        def __call__(self) -> Messenger:
            return messenger

    messenger = WhatsAppMessenger()
    add_factory(MessengerFactory, WhatsAppMessengerFactory())
