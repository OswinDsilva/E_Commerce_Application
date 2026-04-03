from datetime import date
from typing import Any

from ..errors import ApiError
from .common import require_int, require_iso_date, require_text, serialize_date


def _serialize_account(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "acc_no": row["acc_no"],
        "bank_name": row["bank_name"],
        "expiry_date": serialize_date(row["expiry_date"]),
        "u_id": row["u_id"],
    }


def list_bank_accounts(connection: Any, current_user: dict[str, Any]) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT acc_no, bank_name, expiry_date, u_id
            FROM Bank_acc
            WHERE u_id = %s
            ORDER BY acc_no
            """,
            (current_user["u_id"],),
        )
        rows = cursor.fetchall()

    return [_serialize_account(row) for row in rows]


def add_bank_account(
    connection: Any,
    account_data: dict[str, Any],
    current_user: dict[str, Any],
) -> dict[str, Any]:
    acc_no = require_int(account_data.get("acc_no"), "acc_no")
    bank_name = require_text(account_data.get("bank_name"), "bank_name")
    expiry_date = require_iso_date(account_data.get("expiry_date"), "expiry_date")

    if expiry_date < date.today():
        raise ApiError(
            "expiry_date cannot be in the past",
            "BAD_REQUEST",
            400,
        )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT acc_no FROM Bank_acc WHERE acc_no = %s LIMIT 1",
            (acc_no,),
        )
        existing = cursor.fetchone()

    if existing:
        raise ApiError("Bank account already exists", "BAD_REQUEST", 400)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Bank_acc (acc_no, bank_name, expiry_date, u_id)
            VALUES (%s, %s, %s, %s)
            """,
            (acc_no, bank_name, expiry_date, current_user["u_id"]),
        )

    return {
        "acc_no": acc_no,
        "bank_name": bank_name,
        "expiry_date": expiry_date.isoformat(),
        "u_id": current_user["u_id"],
    }


def delete_bank_account(
    connection: Any,
    acc_no: int,
    current_user: dict[str, Any],
) -> None:
    safe_acc_no = require_int(acc_no, "acc_no")

    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Bank_acc WHERE acc_no = %s AND u_id = %s",
            (safe_acc_no, current_user["u_id"]),
        )
        deleted = cursor.rowcount

    if deleted != 1:
        raise ApiError("Bank account not found", "NOT_FOUND", 404)
