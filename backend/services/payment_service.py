from datetime import date
from typing import Any

from ..errors import ApiError
from ..utils.auth import require_same_user
from .common import require_int, serialize_date, serialize_decimal


def _serialize_order(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "o_id": row["o_id"],
        "order_date": serialize_date(row["order_date"]),
        "status": row["status"],
        "total_amount": serialize_decimal(row["total_amount"]),
        "u_id": row["u_id"],
        "acc_no": row["acc_no"],
    }


def _serialize_invoice(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None

    return {
        "i_id": row["i_id"],
        "invoice_date": serialize_date(row["invoice_date"]),
        "total_amount": serialize_decimal(row["total_amount"]),
        "shipping_address": row["shipping_address"],
        "billing_address": row["billing_address"],
        "o_id": row["o_id"],
    }


def pay_for_order(
    connection: Any,
    o_id: int,
    acc_no: Any,
    current_user: dict[str, Any],
) -> dict[str, Any]:
    order_id = require_int(o_id, "o_id")
    account_number = require_int(acc_no, "acc_no")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT o_id, order_date, status, total_amount, u_id, acc_no
            FROM Orders
            WHERE o_id = %s
            FOR UPDATE
            """,
            (order_id,),
        )
        order = cursor.fetchone()

        if not order:
            raise ApiError("Order not found", "NOT_FOUND", 404)

        require_same_user(order["u_id"], current_user)

        if order["status"] == "PAID":
            raise ApiError("Order has already been paid", "ALREADY_PAID", 409)

        if order["status"] != "CREATED":
            raise ApiError(
                "Order cannot be paid in its current state",
                "BAD_REQUEST",
                400,
            )

        cursor.execute(
            """
            SELECT acc_no, bank_name, expiry_date, u_id
            FROM Bank_acc
            WHERE acc_no = %s
            LIMIT 1
            """,
            (account_number,),
        )
        account = cursor.fetchone()

        if not account or account["u_id"] != current_user["u_id"]:
            raise ApiError("Selected bank account is invalid", "INVALID_ACCOUNT", 400)

        if account["expiry_date"] < date.today():
            raise ApiError("Selected bank account is invalid", "INVALID_ACCOUNT", 400)

        cursor.execute(
            """
            UPDATE Orders
            SET status = 'PAID', acc_no = %s
            WHERE o_id = %s AND status = 'CREATED'
            """,
            (account_number, order_id),
        )

        if cursor.rowcount != 1:
            raise ApiError("Order has already been paid", "ALREADY_PAID", 409)

        cursor.execute(
            """
            SELECT o_id, order_date, status, total_amount, u_id, acc_no
            FROM Orders
            WHERE o_id = %s
            LIMIT 1
            """,
            (order_id,),
        )
        updated_order = cursor.fetchone()

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

    return {
        "order": _serialize_order(updated_order),
        "invoice": _serialize_invoice(invoice),
    }
