__all__ = [
    "Messenger",
    "MessengerFactory",
]


class Messenger:
    def send_message(self, name: str, message: str) -> None:
        raise NotImplementedError()


class MessengerFactory:
    def __call__(self) -> Messenger:
        raise NotImplementedError()
