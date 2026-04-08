from fastapi import APIRouter, Depends, Request, status
from pymysql.connections import Connection

from ..database import get_db
from ..schemas.orders import (
    OrderCreateRequest,
    OrderDetailResponse,
    OrderItemsUpdateRequest,
    OrderListResponse,
    OrderResponse,
)
from ..schemas.users import AuthenticatedUser
from ..services.order_service import (
    add_items_to_order,
    create_order,
    get_order_by_id,
    list_order_items,
    list_orders,
)
from ..utils.auth import require_auth


router = APIRouter(prefix="/orders", tags=["orders"])


def _current_user(request: Request, db: Connection = Depends(get_db)) -> AuthenticatedUser:
    return require_auth(request, db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def add_order(
    payload: OrderCreateRequest,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> OrderResponse:
    return OrderResponse(order=create_order(db, payload, current_user))


@router.get("", response_model=OrderListResponse)
def get_orders(
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> OrderListResponse:
    return OrderListResponse(orders=list_orders(db, current_user))


@router.get("/{o_id}", response_model=OrderDetailResponse)
def get_order(
    o_id: int,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> OrderDetailResponse:
    return OrderDetailResponse(
        order=get_order_by_id(db, o_id, current_user),
        items=list_order_items(db, o_id, current_user),
    )


@router.post("/{o_id}/items", response_model=OrderResponse)
def add_order_items(
    o_id: int,
    payload: OrderItemsUpdateRequest,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> OrderResponse:
    return OrderResponse(order=add_items_to_order(db, o_id, payload, current_user))
