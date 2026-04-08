from fastapi import APIRouter, Depends, Request
from pymysql.connections import Connection

from ..database import get_db
from ..schemas.payments import PayOrderRequest, PayOrderResponse
from ..schemas.users import AuthenticatedUser
from ..services.payment_service import get_invoice_for_order, pay_for_order
from ..utils.auth import require_auth


router = APIRouter(prefix="/orders", tags=["payments"])


def _current_user(request: Request, db: Connection = Depends(get_db)) -> AuthenticatedUser:
    return require_auth(request, db)


@router.post("/{o_id}/pay", response_model=PayOrderResponse)
def pay_order(
    o_id: int,
    payload: PayOrderRequest,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> PayOrderResponse:
    return pay_for_order(db, o_id, payload, current_user)


@router.get("/{o_id}/invoice", response_model=PayOrderResponse)
def get_order_invoice(
    o_id: int,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> PayOrderResponse:
    return get_invoice_for_order(db, o_id, current_user)
