from uuid import UUID

from fastapi_integration.token_encoders import TokenEncoder, TokenEncoderFactory
from galo_ioc import add_factory

__all__ = [
    "FakeTokenEncoder",
]


class FakeTokenEncoder(TokenEncoder):
    def encode(self, user_id: UUID) -> str:
        return str(user_id)

    def decode(self, token: str) -> UUID:
        return UUID(token)


def load() -> None:
    class FakeTokenEncoderFactory(TokenEncoderFactory):
        def __call__(self) -> TokenEncoder:
            return token_encoder

    token_encoder = FakeTokenEncoder()
    add_factory(TokenEncoderFactory, FakeTokenEncoderFactory())
