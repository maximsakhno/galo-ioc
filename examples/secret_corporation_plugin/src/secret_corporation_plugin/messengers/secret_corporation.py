from ioc import add_factory
from congratulations_app.messengers import Messenger, MessengerFactory


__all__ = [
    "SecretCorporationMessenger",
    "load",
]


class SecretCorporationMessenger(Messenger):
    def send_message(self, name: str, message: str) -> None:
        print(f"Message {message!r} sent to {name!r} via Secret Corporation Messenger.")


def load() -> None:
    class SecretCorporationMessengerFactory(MessengerFactory):
        def __call__(self) -> Messenger:
            return messenger

    messenger = SecretCorporationMessenger()
    add_factory(MessengerFactory, SecretCorporationMessengerFactory())
