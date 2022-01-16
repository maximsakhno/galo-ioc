from uuid import UUID

__all__ = [
    "TokenEncoder",
    "TokenEncoderFactory",
]


class TokenEncoder:
    def encode(self, user_id: UUID) -> str:
        raise NotImplementedError()

    def decode(self, token: str) -> UUID:
        raise NotImplementedError()


class TokenEncoderFactory:
    def __call__(self) -> TokenEncoder:
        raise NotImplementedError()
