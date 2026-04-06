import secrets
import threading

from ..schemas.users import AuthenticatedUser, UserOut


_SESSIONS: dict[str, int] = {}
_LOCK = threading.RLock()


def create_session(user: UserOut | AuthenticatedUser | dict[str, object]) -> str:
    session_token = secrets.token_urlsafe(32)
    user_id = getattr(user, "u_id", None)
    if user_id is None:
        user_id = user["u_id"]

    with _LOCK:
        _SESSIONS[session_token] = int(user_id)
    return session_token


def get_session_user_id(session_token: str | None) -> int | None:
    if not session_token:
        return None

    with _LOCK:
        return _SESSIONS.get(session_token)


def destroy_session(session_token: str | None) -> None:
    if not session_token:
        return

    with _LOCK:
        _SESSIONS.pop(session_token, None)


def clear_user_sessions(u_id: int) -> None:
    target_id = int(u_id)
    with _LOCK:
        stale_tokens = [
            session_token
            for session_token, session_user_id in _SESSIONS.items()
            if session_user_id == target_id
        ]
        for session_token in stale_tokens:
            _SESSIONS.pop(session_token, None)
