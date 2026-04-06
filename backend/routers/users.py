from fastapi import APIRouter, Depends, Request, Response, status
from pymysql.connections import Connection

from ..database import get_db
from ..schemas.users import AuthenticatedUser, UserResponse
from ..services.user_service import delete_user, get_user_profile
from ..utils.auth import SESSION_COOKIE_NAME, require_auth


router = APIRouter(prefix="/users", tags=["users"])


def _current_user(request: Request, db: Connection = Depends(get_db)) -> AuthenticatedUser:
    return require_auth(request, db)


@router.get("/{u_id}", response_model=UserResponse)
def get_profile(
    u_id: int,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> UserResponse:
    return UserResponse(user=get_user_profile(db, u_id, current_user))


@router.delete("/{u_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(
    u_id: int,
    request: Request,
    response: Response,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> Response:
    delete_user(db, u_id, current_user)
    if current_user.u_id == u_id:
        response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
