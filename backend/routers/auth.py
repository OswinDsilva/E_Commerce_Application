from fastapi import APIRouter, Depends, Request, Response, status
from pymysql.connections import Connection

from ..database import get_db
from ..schemas.auth import LoginRequest, RegisterRequest
from ..schemas.users import UserResponse
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


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(
    response: Response,
    payload: RegisterRequest,
    db: Connection = Depends(get_db),
) -> UserResponse:
    user = register_user(db, payload)
    session_token = create_session(user)
    _set_session_cookie(response, session_token)
    return UserResponse(user=user)


@router.post("/login", response_model=UserResponse)
def login(
    response: Response,
    payload: LoginRequest,
    db: Connection = Depends(get_db),
) -> UserResponse:
    user = login_user(db, payload)
    session_token = create_session(user)
    _set_session_cookie(response, session_token)
    return UserResponse(user=user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
) -> Response:
    logout_user(request.cookies.get(SESSION_COOKIE_NAME))
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserResponse)
def me(
    request: Request,
    db: Connection = Depends(get_db),
) -> UserResponse:
    user = require_auth(request, db)
    return UserResponse(user=user)
