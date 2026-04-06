from typing import Any

from ..errors import ApiError
from ..schemas.auth import LoginRequest, RegisterRequest
from ..schemas.users import AuthenticatedUser, UserOut
from ..utils.passwords import hash_password, verify_password
from ..utils.sessions import destroy_session, get_session_user_id
from .common import call_procedure, get_next_id, require_text


def _build_user_model(row: dict[str, Any], *, authenticated: bool = False) -> UserOut:
    model_cls = AuthenticatedUser if authenticated else UserOut
    return model_cls.model_validate(
        {
            "u_id": row["u_id"],
            "username": row["username"],
            "email": row["email"],
            "phone": row["phone"],
            "created_at": row["created_at"],
            "role_id": row["role_id"],
            "role": row["role"],
        }
    )


def _fetch_user_by_username(
    connection: Any,
    username: str,
    include_password: bool = False,
) -> dict[str, Any] | None:
    password_select = ", u.password_hash" if include_password else ""
    query = f"""
        SELECT
            u.u_id,
            u.username,
            u.email,
            u.phone,
            u.created_at,
            u.role_id,
            r.role
            {password_select}
        FROM Users u
        INNER JOIN roles r ON r.id = u.role_id
        WHERE u.username = %s
        LIMIT 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone()


def fetch_user_by_id(
    connection: Any,
    u_id: int,
    include_password: bool = False,
) -> dict[str, Any] | None:
    password_select = ", u.password_hash" if include_password else ""
    query = f"""
        SELECT
            u.u_id,
            u.username,
            u.email,
            u.phone,
            u.created_at,
            u.role_id,
            r.role
            {password_select}
        FROM Users u
        INNER JOIN roles r ON r.id = u.role_id
        WHERE u.u_id = %s
        LIMIT 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (u_id,))
        return cursor.fetchone()


def _get_default_user_role_id(connection: Any) -> int:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM roles WHERE role = %s LIMIT 1", ("USER",))
        row = cursor.fetchone()

    if not row:
        raise ApiError(
            "Default USER role is not configured in roles table",
            "SERVER_ERROR",
            500,
        )

    return int(row["id"])


def _validate_register_payload(payload: RegisterRequest) -> tuple[str, str, str, str]:
    username = require_text(payload.username, "username")
    password = require_text(payload.password, "password")
    email = require_text(payload.email, "email")
    phone = require_text(payload.phone, "phone")

    if len(password) < 6:
        raise ApiError(
            "Password must be at least 6 characters long",
            "BAD_REQUEST",
            400,
        )

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ApiError("email must be valid", "BAD_REQUEST", 400)

    return username, password, email, phone


def register_user(connection: Any, data: RegisterRequest) -> UserOut:
    username, password, email, phone = _validate_register_payload(data)

    u_id = get_next_id(connection, "Users", "u_id")
    role_id = _get_default_user_role_id(connection)
    password_hash = hash_password(password)

    user = call_procedure(
        connection,
        "CALL sp_register_user(%s, %s, %s, %s, %s, %s)",
        (u_id, username, password_hash, email, phone, role_id),
        fetch="one",
    )
    if not user:
        raise ApiError("Unable to create user", "SERVER_ERROR", 500)

    return _build_user_model(user, authenticated=True)


def login_user(connection: Any, credentials: LoginRequest) -> AuthenticatedUser:
    safe_username = require_text(credentials.username, "username")
    safe_password = require_text(credentials.password, "password")
    user = _fetch_user_by_username(connection, safe_username, include_password=True)

    if not user or not verify_password(safe_password, user["password_hash"]):
        raise ApiError("Invalid username or password", "UNAUTHORIZED", 401)

    return _build_user_model(user, authenticated=True)


def logout_user(session_token: str | None) -> None:
    if session_token:
        destroy_session(session_token)


def get_current_user(connection: Any, session_token: str | None) -> AuthenticatedUser:
    if not session_token:
        raise ApiError("Authentication required", "UNAUTHORIZED", 401)

    u_id = get_session_user_id(session_token)
    if u_id is None:
        raise ApiError("Authentication required", "UNAUTHORIZED", 401)

    user = fetch_user_by_id(connection, u_id)
    if not user:
        destroy_session(session_token)
        raise ApiError("Authentication required", "UNAUTHORIZED", 401)

    return _build_user_model(user, authenticated=True)
