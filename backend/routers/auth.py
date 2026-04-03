from typing import Any

from fastapi import APIRouter, Body, Depends, Request, Response, status
from pymysql.connections import Connection

from ..database import get_db
from ..services.auth_service import (
    login_user,
    logout_user,
    register_user,
)
from ..utils.auth import SESSION_COOKIE_NAME, require_auth
from ..utils.sessions import create_session


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        path="/",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    response: Response,
    payload: dict[str, Any] = Body(...),
    db: Connection = Depends(get_db),
) -> dict[str, Any]:
    user = register_user(db, payload)
    session_token = create_session(user)
    _set_session_cookie(response, session_token)
    return {"user": user}


@router.post("/login")
def login(
    response: Response,
    payload: dict[str, Any] = Body(...),
    db: Connection = Depends(get_db),
) -> dict[str, Any]:
    user = login_user(db, payload.get("username"), payload.get("password"))
    session_token = create_session(user)
    _set_session_cookie(response, session_token)
    return {"user": user}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
) -> Response:
    logout_user(request.cookies.get(SESSION_COOKIE_NAME))
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me")
def me(
    request: Request,
    db: Connection = Depends(get_db),
) -> dict[str, Any]:
    user = require_auth(request, db)
    return {"user": user}
