from fastapi_integration.models import Entity
from pydantic import BaseModel

__all__ = [
    "BaseUser",
    "UserToCreate",
    "UserToUpdate",
    "User",
    "PrivateUser",
    "convert_private_user_to_user",
]


class HasPassword(BaseModel):
    password: str


class BaseUser(BaseModel):
    login: str
    role: str


class UserToCreate(BaseUser, HasPassword):
    pass


class UserToUpdate(BaseUser, HasPassword):
    pass


class User(Entity, BaseUser):
    pass


class PrivateUser(Entity, BaseUser, HasPassword):
    pass


def convert_private_user_to_user(private_user: PrivateUser) -> User:
    return User(
        id=private_user.id,
        created_at=private_user.created_at,
        updated_at=private_user.updated_at,
        login=private_user.login,
        role=private_user.role,
    )
