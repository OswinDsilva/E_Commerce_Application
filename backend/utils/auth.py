from typing import Any

from ..errors import ApiError
from ..schemas.users import AuthenticatedUser
from ..services.auth_service import get_current_user


SESSION_COOKIE_NAME = "session_token"


def get_session_user(request: Any, connection: Any) -> AuthenticatedUser:
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    return get_current_user(connection, session_token)


def require_auth(request: Any, connection: Any) -> AuthenticatedUser:
    return get_session_user(request, connection)


def require_same_user(
    resource_user_id: int,
    current_user: AuthenticatedUser,
    allow_admin: bool = False,
) -> None:
    if allow_admin and current_user.role == "ADMIN":
        return

    if int(resource_user_id) != int(current_user.u_id):
        raise ApiError("You are not allowed to access this resource", "UNAUTHORIZED", 403)
