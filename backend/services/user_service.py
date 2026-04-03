from typing import Any

from ..errors import ApiError
from ..utils.auth import require_same_user
from ..utils.sessions import clear_user_sessions
from .auth_service import fetch_user_by_id, serialize_user


def get_user_profile(
    connection: Any,
    requested_u_id: int,
    current_user: dict[str, Any],
) -> dict[str, Any]:
    require_same_user(requested_u_id, current_user)
    user = fetch_user_by_id(connection, requested_u_id)

    if not user:
        raise ApiError("User not found", "NOT_FOUND", 404)

    return serialize_user(user)


def delete_user(
    connection: Any,
    requested_u_id: int,
    current_user: dict[str, Any],
) -> None:
    require_same_user(requested_u_id, current_user)

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Users WHERE u_id = %s", (requested_u_id,))
        deleted = cursor.rowcount

    if deleted != 1:
        raise ApiError("User not found", "NOT_FOUND", 404)

    clear_user_sessions(requested_u_id)
