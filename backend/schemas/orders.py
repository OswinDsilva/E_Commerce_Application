from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints, field_serializer

from .base import AppBaseModel

class OrderItemIn(AppBaseModel):
    p_id: int
    quantity: int = Field(gt=0)


class OrderCreateRequest(AppBaseModel):
    items: list[OrderItemIn] = Field(min_length=1)
    shipping_address: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    billing_address: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class OrderItemsUpdateRequest(AppBaseModel):
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(AppBaseModel):
    p_id: int
    product_name: str
    quantity: int
    price_at_purchase: Decimal
    line_total: Decimal

    @field_serializer("price_at_purchase", "line_total")
    def serialize_amounts(self, value: Decimal) -> float:
        return float(value)


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


class OrderResponse(AppBaseModel):
    order: OrderOut


class OrderListResponse(AppBaseModel):
    orders: list[OrderOut]


class OrderDetailResponse(AppBaseModel):
    order: OrderOut
    items: list[OrderItemOut]
