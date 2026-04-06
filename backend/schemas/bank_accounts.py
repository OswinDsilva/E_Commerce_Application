from datetime import date
from typing import Annotated

from pydantic import StringConstraints, field_validator

from .base import AppBaseModel


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CreateBankAccountRequest(AppBaseModel):
    acc_no: int
    bank_name: NonEmptyStr
    expiry_date: date

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("expiry_date cannot be in the past")
        return value


class BankAccountOut(AppBaseModel):
    acc_no: int
    bank_name: str
    expiry_date: date
    u_id: int


class BankAccountResponse(AppBaseModel):
    account: BankAccountOut


class BankAccountListResponse(AppBaseModel):
    accounts: list[BankAccountOut]
