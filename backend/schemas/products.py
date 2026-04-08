from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from .base import AppBaseModel


class CategoryCreateRequest(AppBaseModel):
    category: str = Field(min_length=1)


class CategoryOut(AppBaseModel):
    id: int
    category: str


class CategoryListResponse(AppBaseModel):
    categories: list[CategoryOut]


class CategoryResponse(AppBaseModel):
    category: CategoryOut


class ProductBaseRequest(AppBaseModel):
    product_name: str = Field(min_length=1)
    brand: str = Field(min_length=1)
    price: Decimal = Field(ge=0)
    category_id: int
    description: str = Field(min_length=1)


class ProductCreateRequest(ProductBaseRequest):
    quantity: int = Field(default=0, ge=0)


class ProductUpdateRequest(ProductBaseRequest):
    pass


class InventoryUpdateRequest(AppBaseModel):
    quantity: int = Field(ge=0)


class StockDeductRequest(AppBaseModel):
    quantity: int = Field(gt=0)


class ProductOut(AppBaseModel):
    p_id: int
    product_name: str
    brand: str
    price: Decimal
    category_id: int
    category_name: str | None = None
    description: str
    quantity: int = 0
    stock_status: str
    last_updated: datetime | None = None

    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> float:
        return float(value)


class ProductListResponse(AppBaseModel):
    products: list[ProductOut]


class ProductResponse(AppBaseModel):
    product: ProductOut
