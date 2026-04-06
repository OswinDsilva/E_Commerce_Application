from fastapi import APIRouter, Depends, Request, Response, status
from pymysql.connections import Connection

from ..database import get_db
from ..schemas.bank_accounts import (
    BankAccountListResponse,
    BankAccountResponse,
    CreateBankAccountRequest,
)
from ..schemas.users import AuthenticatedUser
from ..services.bank_account_service import (
    add_bank_account,
    delete_bank_account,
    list_bank_accounts,
)
from ..utils.auth import require_auth


router = APIRouter(prefix="/bank-accounts", tags=["bank-accounts"])


def _current_user(request: Request, db: Connection = Depends(get_db)) -> AuthenticatedUser:
    return require_auth(request, db)


@router.get("", response_model=BankAccountListResponse)
def get_accounts(
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> BankAccountListResponse:
    return BankAccountListResponse(accounts=list_bank_accounts(db, current_user))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BankAccountResponse)
def create_account(
    payload: CreateBankAccountRequest,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> BankAccountResponse:
    return BankAccountResponse(account=add_bank_account(db, payload, current_user))


@router.delete("/{acc_no}", status_code=status.HTTP_204_NO_CONTENT)
def remove_account(
    acc_no: int,
    current_user: AuthenticatedUser = Depends(_current_user),
    db: Connection = Depends(get_db),
) -> Response:
    delete_bank_account(db, acc_no, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
