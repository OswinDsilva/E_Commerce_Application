from datetime import date
from decimal import Decimal

from pydantic import field_serializer

from .base import AppBaseModel


class PayOrderRequest(AppBaseModel):
    acc_no: int


class OrderOut(AppBaseModel):
    o_id: int
    order_date: date
    status: str
    total_amount: Decimal
    u_id: int
    acc_no: int | None

    @field_serializer("total_amount")
    def serialize_total_amount(self, value: Decimal) -> float:
        return float(value)


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
