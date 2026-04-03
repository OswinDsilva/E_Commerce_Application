from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    product_name: str
    brand: str
    price: float = Field(ge=0)
    category: int
    description: str
    quantity: int = Field(ge=0, default=0)

class ProductResponse(BaseModel):
    p_id: int
    product_name: str
    brand: str
    price: float
    category: int
    description: str
    quantity: Optional[int] = None
    stock_status: Optional[str] = None

    class Config:
        from_attributes = True

class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)

class StockDeduct(BaseModel):
    quantity: int = Field(gt=0)

class ProductUpdate(BaseModel):
    product_name: str
    brand: str
    price: float = Field(ge=0)
    category: int
    description: str