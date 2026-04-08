import json
from typing import Any

from ..errors import ApiError
from ..schemas.orders import OrderCreateRequest, OrderItemOut, OrderItemsUpdateRequest, OrderOut
from ..schemas.users import AuthenticatedUser
from ..utils.auth import require_same_user
from .common import call_procedure


ORDER_COLUMNS = "o_id, order_date, status, total_amount, u_id, acc_no"
ORDER_REQUIRED_FIELDS = {"o_id", "order_date", "status", "total_amount", "u_id", "acc_no"}


def _build_order_model(row: dict[str, Any]) -> OrderOut:
    return OrderOut.model_validate(row)


def _build_order_item_model(row: dict[str, Any]) -> OrderItemOut:
    return OrderItemOut.model_validate(row)


def _extract_order_row(result: Any) -> dict[str, Any] | None:
    if isinstance(result, dict) and ORDER_REQUIRED_FIELDS.issubset(result.keys()):
        return result

    if isinstance(result, list):
        for row in result:
            if isinstance(row, dict) and ORDER_REQUIRED_FIELDS.issubset(row.keys()):
                return row

    return None


def _items_to_json(items: list[Any]) -> str:
    return json.dumps([{"p_id": int(item.p_id), "quantity": int(item.quantity)} for item in items])


def _fetch_order_row(connection: Any, o_id: int) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {ORDER_COLUMNS}
            FROM Orders
            WHERE o_id = %s
            LIMIT 1
            """,
            (o_id,),
        )
        return cursor.fetchone()


def create_order(
    connection: Any,
    payload: OrderCreateRequest,
    current_user: AuthenticatedUser,
) -> OrderOut:
    procedure_result = call_procedure(
        connection,
        "CALL sp_create_order_with_items(%s, %s, %s, %s)",
        (
            current_user.u_id,
            payload.shipping_address,
            payload.billing_address,
            _items_to_json(payload.items),
        ),
        fetch="all",
    )

    created = _extract_order_row(procedure_result)

    if not created:
        raise ApiError("Unable to create order", "SERVER_ERROR", 500)

    return _build_order_model(created)


def add_items_to_order(
    connection: Any,
    o_id: int,
    payload: OrderItemsUpdateRequest,
    current_user: AuthenticatedUser,
) -> OrderOut:
    procedure_result = call_procedure(
        connection,
        "CALL sp_add_order_items(%s, %s, %s)",
        (int(o_id), current_user.u_id, _items_to_json(payload.items)),
        fetch="all",
    )

    updated = _extract_order_row(procedure_result)

    if not updated:
        raise ApiError("Unable to update order items", "SERVER_ERROR", 500)

    return _build_order_model(updated)


def get_order_by_id(connection: Any, o_id: int, current_user: AuthenticatedUser) -> OrderOut:
    order_id = int(o_id)
    row = _fetch_order_row(connection, order_id)
    if not row:
        raise ApiError("Order not found", "NOT_FOUND", 404)

    require_same_user(row["u_id"], current_user, allow_admin=True)
    return _build_order_model(row)


def list_orders(connection: Any, current_user: AuthenticatedUser) -> list[OrderOut]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {ORDER_COLUMNS}
            FROM Orders
            WHERE u_id = %s
            ORDER BY order_date DESC, o_id DESC
            """,
            (current_user.u_id,),
        )
        rows = cursor.fetchall()

    return [_build_order_model(row) for row in rows]


def list_order_items(connection: Any, o_id: int, current_user: AuthenticatedUser) -> list[OrderItemOut]:
    order = _fetch_order_row(connection, int(o_id))
    if not order:
        raise ApiError("Order not found", "NOT_FOUND", 404)

    require_same_user(order["u_id"], current_user, allow_admin=True)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                oi.p_id,
                p.product_name,
                oi.quantity,
                oi.price_at_purchase,
                (oi.quantity * oi.price_at_purchase) AS line_total
            FROM ordered_items oi
            INNER JOIN Products p ON p.p_id = oi.p_id
            WHERE oi.o_id = %s
            ORDER BY oi.p_id
            """,
            (int(o_id),),
        )
        rows = cursor.fetchall()

    return [_build_order_item_model(row) for row in rows]
