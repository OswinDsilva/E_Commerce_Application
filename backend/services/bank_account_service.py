from datetime import date
from typing import Any

from ..errors import ApiError
from ..schemas.bank_accounts import BankAccountOut, CreateBankAccountRequest
from ..schemas.users import AuthenticatedUser
from .common import call_procedure


def _build_account_model(row: dict[str, Any]) -> BankAccountOut:
    return BankAccountOut.model_validate(row)


def list_bank_accounts(connection: Any, current_user: AuthenticatedUser) -> list[BankAccountOut]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT acc_no, bank_name, expiry_date, u_id
            FROM Bank_acc
            WHERE u_id = %s
            ORDER BY acc_no
            """,
            (current_user.u_id,),
        )
        rows = cursor.fetchall()

    return [_build_account_model(row) for row in rows]


def add_bank_account(
    connection: Any,
    account_data: CreateBankAccountRequest,
    current_user: AuthenticatedUser,
) -> BankAccountOut:
    acc_no = account_data.acc_no
    bank_name = account_data.bank_name
    expiry_date = account_data.expiry_date

    if expiry_date < date.today():
        raise ApiError(
            "expiry_date cannot be in the past",
            "BAD_REQUEST",
            400,
        )

    account = call_procedure(
        connection,
        "CALL sp_create_bank_account(%s, %s, %s, %s)",
        (acc_no, bank_name, expiry_date, current_user.u_id),
        fetch="one",
    )

    if not account:
        raise ApiError("Unable to create bank account", "SERVER_ERROR", 500)

    return _build_account_model(account)


def delete_bank_account(
    connection: Any,
    acc_no: int,
    current_user: AuthenticatedUser,
) -> None:
    call_procedure(
        connection,
        "CALL sp_delete_bank_account(%s, %s)",
        (int(acc_no), current_user.u_id),
        fetch="one",
    )
