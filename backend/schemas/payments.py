from datetime import date
from decimal import Decimal

from pydantic import field_serializer

from .base import AppBaseModel
from .orders import OrderOut


class PayOrderRequest(AppBaseModel):
    acc_no: int


class InvoiceOut(AppBaseModel):
    i_id: int
    invoice_date: date
    total_amount: Decimal
    shipping_address: str
    billing_address: str
    o_id: int

    @field_serializer("total_amount")
    def serialize_total_amount(self, value: Decimal) -> float:
        return float(value)


class PayOrderResponse(AppBaseModel):
    order: OrderOut
    invoice: InvoiceOut | None
