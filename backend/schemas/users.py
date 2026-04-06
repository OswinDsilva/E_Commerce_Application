from datetime import datetime

from .base import AppBaseModel


class UserOut(AppBaseModel):
    u_id: int
    username: str
    email: str
    phone: str
    created_at: datetime
    role_id: int
    role: str


class AuthenticatedUser(UserOut):
    pass


class UserResponse(AppBaseModel):
    user: UserOut
