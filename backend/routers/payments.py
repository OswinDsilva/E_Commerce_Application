from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from pymysql.connections import Connection

from ..database import get_db
from ..services.payment_service import pay_for_order
from ..utils.auth import require_auth


router = APIRouter(prefix="/orders", tags=["payments"])


def _current_user(request: Request, db: Connection = Depends(get_db)) -> dict[str, Any]:
    return require_auth(request, db)


@router.post("/{o_id}/pay")
def pay_order(
    o_id: int,
    payload: dict[str, Any] = Body(...),
    current_user: dict[str, Any] = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> dict[str, Any]:
    return pay_for_order(db, o_id, payload.get("acc_no"), current_user)
