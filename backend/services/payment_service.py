from typing import Any

from ..errors import ApiError
from ..schemas.payments import InvoiceOut, OrderOut, PayOrderRequest, PayOrderResponse
from ..schemas.users import AuthenticatedUser
from .common import call_procedure


def _build_order_model(row: dict[str, Any]) -> OrderOut:
    return OrderOut.model_validate(row)


def _build_invoice_model(row: dict[str, Any] | None) -> InvoiceOut | None:
    if row is None:
        return None

    return InvoiceOut.model_validate(row)


def pay_for_order(
    connection: Any,
    o_id: int,
    payload: PayOrderRequest,
    current_user: AuthenticatedUser,
) -> PayOrderResponse:
    order_id = int(o_id)
    account_number = payload.acc_no

    updated_order = call_procedure(
        connection,
        "CALL sp_pay_order(%s, %s, %s)",
        (order_id, current_user.u_id, account_number),
        fetch="one",
    )

    if not updated_order:
        raise ApiError("Unable to update order payment status", "SERVER_ERROR", 500)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT i_id, invoice_date, total_amount, shipping_address, billing_address, o_id
            FROM Invoice
            WHERE o_id = %s
            LIMIT 1
            """,
            (order_id,),
        )
        invoice = cursor.fetchone()

    return PayOrderResponse(
        order=_build_order_model(updated_order),
        invoice=_build_invoice_model(invoice),
    )
