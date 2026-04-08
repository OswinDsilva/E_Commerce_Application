from fastapi import APIRouter, Depends, Response, status
from pymysql.connections import Connection

from ..database import get_db
from ..errors import ApiError
from ..schemas.products import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    InventoryUpdateRequest,
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
    StockDeductRequest,
)
from ..services.product_service import (
    create_category,
    create_product,
    deduct_stock,
    delete_product,
    get_product_by_id,
    list_categories,
    list_products,
    update_inventory,
    update_product,
)


router = APIRouter(prefix="/products", tags=["products"])
category_router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=ProductListResponse)
def get_products(db: Connection = Depends(get_db)) -> ProductListResponse:
    return ProductListResponse(products=list_products(db))


@router.get("/{p_id}", response_model=ProductResponse)
def get_product(p_id: int, db: Connection = Depends(get_db)) -> ProductResponse:
    product = get_product_by_id(db, p_id)
    if not product:
        raise ApiError("Product not found", "NOT_FOUND", 404)
    return ProductResponse(product=product)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def add_product(
    payload: ProductCreateRequest,
    db: Connection = Depends(get_db),
) -> ProductResponse:
    return ProductResponse(product=create_product(db, payload))


@router.put("/{p_id}", response_model=ProductResponse)
def edit_product(
    p_id: int,
    payload: ProductUpdateRequest,
    db: Connection = Depends(get_db),
) -> ProductResponse:
    product = update_product(db, p_id, payload)
    if not product:
        raise ApiError("Product not found", "NOT_FOUND", 404)
    return ProductResponse(product=product)


@router.delete("/{p_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(
    p_id: int,
    db: Connection = Depends(get_db),
) -> Response:
    deleted = delete_product(db, p_id)
    if not deleted:
        raise ApiError("Product not found", "NOT_FOUND", 404)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{p_id}/inventory", response_model=ProductResponse)
def edit_stock(
    p_id: int,
    payload: InventoryUpdateRequest,
    db: Connection = Depends(get_db),
) -> ProductResponse:
    product = update_inventory(db, p_id, payload.quantity)
    if not product:
        raise ApiError("Product not found", "NOT_FOUND", 404)
    return ProductResponse(product=product)


@router.post("/{p_id}/deduct", response_model=ProductResponse)
def deduct_product_inventory(
    p_id: int,
    payload: StockDeductRequest,
    db: Connection = Depends(get_db),
) -> ProductResponse:
    return ProductResponse(product=deduct_stock(db, p_id, payload.quantity))


@category_router.get("", response_model=CategoryListResponse)
def get_categories(db: Connection = Depends(get_db)) -> CategoryListResponse:
    return CategoryListResponse(categories=list_categories(db))


@category_router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
def add_category(
    payload: CategoryCreateRequest,
    db: Connection = Depends(get_db),
) -> CategoryResponse:
    return CategoryResponse(category=create_category(db, payload.category))
