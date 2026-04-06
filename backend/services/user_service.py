from typing import Any

from ..errors import ApiError
from ..schemas.users import AuthenticatedUser, UserOut
from ..utils.auth import require_same_user
from ..utils.sessions import clear_user_sessions
from .auth_service import _build_user_model, fetch_user_by_id
from .common import call_procedure


def get_user_profile(
    connection: Any,
    requested_u_id: int,
    current_user: AuthenticatedUser,
) -> UserOut:
    require_same_user(requested_u_id, current_user)
    user = fetch_user_by_id(connection, requested_u_id)

    if not user:
        raise ApiError("User not found", "NOT_FOUND", 404)

    return _build_user_model(user)


def delete_user(
    connection: Any,
    requested_u_id: int,
    current_user: AuthenticatedUser,
) -> None:
    require_same_user(requested_u_id, current_user)
    call_procedure(
        connection,
        "CALL sp_delete_user(%s)",
        (requested_u_id,),
        fetch="one",
    )

    clear_user_sessions(requested_u_id)
