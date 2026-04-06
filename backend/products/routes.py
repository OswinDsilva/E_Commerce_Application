from fastapi import APIRouter, Depends, HTTPException
from pymysql.connections import Connection
from . import crud, schemas
from backend.database import get_db

# ── PRODUCTS ROUTER ──────────────────────────────
router = APIRouter(prefix="/products", tags=["Products and Inventory"])

@router.get("/")
def list_all_products(db: Connection = Depends(get_db)):
    return crud.get_all_products(db)

@router.get("/{p_id}")
def get_product(p_id: int, db: Connection = Depends(get_db)):
    product = crud.get_product_by_id(db, p_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/")
def create_product(product: schemas.ProductCreate, db: Connection = Depends(get_db)):
    return crud.add_product(db, product)

@router.put("/{p_id}")
def update_product(p_id: int, body: schemas.ProductUpdate, db: Connection = Depends(get_db)):
    result = crud.update_product(db, p_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated", "p_id": p_id}

@router.delete("/{p_id}")
def delete_product(p_id: int, db: Connection = Depends(get_db)):
    result = crud.soft_delete_product(db, p_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product removed from catalog", "p_id": p_id}

@router.put("/{p_id}/inventory")
def update_stock(p_id: int, body: schemas.InventoryUpdate, db: Connection = Depends(get_db)):
    result = crud.update_inventory(db, p_id, body.quantity)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Stock updated", "p_id": p_id, "new_quantity": body.quantity}

@router.post("/{p_id}/deduct")
def deduct_product_stock(p_id: int, body: schemas.StockDeduct, db: Connection = Depends(get_db)):
    try:
        result = crud.deduct_stock(db, p_id, body.quantity)
        remaining = result.get("quantity", 0) if result else 0
        return {"message": "Stock deducted", "p_id": p_id, "remaining": remaining}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── CATEGORIES ROUTER ────────────────────────────
cat_router = APIRouter(prefix="/categories", tags=["Categories"])

@cat_router.get("/")
def list_categories(db: Connection = Depends(get_db)):
    cats = crud.get_all_categories(db)
    return [{"id": c['id'], "category": c['category']} for c in cats] if cats else []

@cat_router.post("/")
def add_category(body: schemas.CategoryCreate, db: Connection = Depends(get_db)):
    return crud.add_category(db, body.category)