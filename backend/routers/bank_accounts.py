from typing import Any

from fastapi import APIRouter, Body, Depends, Request, Response, status
from pymysql.connections import Connection

from ..database import get_db
from ..services.bank_account_service import (
    add_bank_account,
    delete_bank_account,
    list_bank_accounts,
)
from ..utils.auth import require_auth


router = APIRouter(prefix="/bank-accounts", tags=["bank-accounts"])


def _current_user(request: Request, db: Connection = Depends(get_db)) -> dict[str, Any]:
    return require_auth(request, db)


@router.get("")
def get_accounts(
    current_user: dict[str, Any] = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> dict[str, Any]:
    return {"accounts": list_bank_accounts(db, current_user)}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_account(
    payload: dict[str, Any] = Body(...),
    current_user: dict[str, Any] = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> dict[str, Any]:
    return {"account": add_bank_account(db, payload, current_user)}


@router.delete("/{acc_no}", status_code=status.HTTP_204_NO_CONTENT)
def remove_account(
    acc_no: int,
    current_user: dict[str, Any] = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> Response:
    delete_bank_account(db, acc_no, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
