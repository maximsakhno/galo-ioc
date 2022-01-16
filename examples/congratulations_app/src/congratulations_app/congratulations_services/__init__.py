__all__ = [
    "CongratulationsService",
    "CongratulationsServiceFactory",
]


class CongratulationsService:
    def happy_birthday(self, name: str) -> None:
        raise NotImplementedError()


class CongratulationsServiceFactory:
    def __call__(self) -> CongratulationsService:
        raise NotImplementedError()
