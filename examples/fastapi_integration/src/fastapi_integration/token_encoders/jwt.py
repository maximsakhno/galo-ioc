import os
from uuid import UUID

import jwt
from fastapi_integration.token_encoders import TokenEncoder, TokenEncoderFactory
from galo_ioc import add_factory

__all__ = [
    "JwtTokenEncoder",
]


class JwtTokenEncoder(TokenEncoder):
    def __init__(self, secret: str) -> None:
        self.__secret = secret

    def encode(self, user_id: UUID) -> str:
        payload = {"user_id": str(user_id)}
        return jwt.encode(payload, self.__secret, algorithm="HS256")

    def decode(self, token: str) -> UUID:
        payload = jwt.decode(token, self.__secret, algorithms=["HS256"])
        return UUID(payload["user_id"])


def load() -> None:
    class JwtTokenEncoderFactory(TokenEncoderFactory):
        def __call__(self) -> TokenEncoder:
            return token_encoder

    secret = os.getenv("APP_SECRET", "Maria")
    token_encoder = JwtTokenEncoder(secret)
    add_factory(TokenEncoderFactory, JwtTokenEncoderFactory())
