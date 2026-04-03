from typing import Any

from ..errors import ApiError
from ..utils.passwords import hash_password, verify_password
from ..utils.sessions import destroy_session, get_session_user_id
from .common import get_next_id, require_text, serialize_datetime


def serialize_user(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "u_id": row["u_id"],
        "username": row["username"],
        "email": row["email"],
        "phone": row["phone"],
        "created_at": serialize_datetime(row["created_at"]),
        "role_id": row["role_id"],
        "role": row["role"],
    }


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


def _validate_register_payload(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    username = require_text(payload.get("username"), "username")
    password = require_text(payload.get("password"), "password")
    email = require_text(payload.get("email"), "email")
    phone = require_text(payload.get("phone"), "phone")

    if len(password) < 6:
        raise ApiError(
            "Password must be at least 6 characters long",
            "BAD_REQUEST",
            400,
        )

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ApiError("email must be valid", "BAD_REQUEST", 400)

    return username, password, email, phone


def register_user(connection: Any, data: dict[str, Any]) -> dict[str, Any]:
    username, password, email, phone = _validate_register_payload(data)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT username, email
            FROM Users
            WHERE username = %s OR email = %s
            LIMIT 1
            """,
            (username, email),
        )
        existing = cursor.fetchone()

    if existing:
        if existing["username"] == username:
            raise ApiError("Username already exists", "BAD_REQUEST", 400)
        raise ApiError("Email already exists", "BAD_REQUEST", 400)

    u_id = get_next_id(connection, "Users", "u_id")
    role_id = _get_default_user_role_id(connection)
    password_hash = hash_password(password)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Users (u_id, username, password_hash, email, phone, role_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (u_id, username, password_hash, email, phone, role_id),
        )

    user = fetch_user_by_id(connection, u_id)
    if not user:
        raise ApiError("Unable to create user", "SERVER_ERROR", 500)

    return serialize_user(user)


def login_user(connection: Any, username: Any, password: Any) -> dict[str, Any]:
    safe_username = require_text(username, "username")
    safe_password = require_text(password, "password")
    user = _fetch_user_by_username(connection, safe_username, include_password=True)

    if not user or not verify_password(safe_password, user["password_hash"]):
        raise ApiError("Invalid username or password", "UNAUTHORIZED", 401)

    return serialize_user(user)


def logout_user(session_token: str | None) -> None:
    if session_token:
        destroy_session(session_token)


def get_current_user(connection: Any, session_token: str | None) -> dict[str, Any]:
    if not session_token:
        raise ApiError("Authentication required", "UNAUTHORIZED", 401)

    u_id = get_session_user_id(session_token)
    if u_id is None:
        raise ApiError("Authentication required", "UNAUTHORIZED", 401)

    user = fetch_user_by_id(connection, u_id)
    if not user:
        destroy_session(session_token)
        raise ApiError("Authentication required", "UNAUTHORIZED", 401)

    return serialize_user(user)
