from typing import Annotated

from pydantic import StringConstraints, field_validator

from .base import AppBaseModel


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RegisterRequest(AppBaseModel):
    username: NonEmptyStr
    password: Annotated[str, StringConstraints(min_length=6)]
    email: NonEmptyStr
    phone: NonEmptyStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("email must be valid")
        return value


class LoginRequest(AppBaseModel):
    username: NonEmptyStr
    password: NonEmptyStr
