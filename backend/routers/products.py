from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, Response, status
from fastapi import File, UploadFile
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
UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "uploads" / "products"
MAX_THUMBNAIL_SIZE = 2 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


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


@router.post("/upload-thumbnail")
async def upload_product_thumbnail(file: UploadFile = File(...)) -> dict[str, str]:
    content_type = file.content_type or ""
    extension = ALLOWED_IMAGE_TYPES.get(content_type)
    if not extension:
        raise ApiError("Unsupported image format. Use JPG, PNG, or WEBP.", "BAD_REQUEST", 400)

    data = await file.read()
    if not data:
        raise ApiError("Uploaded file is empty", "BAD_REQUEST", 400)
    if len(data) > MAX_THUMBNAIL_SIZE:
        raise ApiError("Image must be 2MB or smaller", "BAD_REQUEST", 400)

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_ROOT / filename
    file_path.write_bytes(data)

    return {"thumbnail_url": f"/uploads/products/{filename}"}


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
