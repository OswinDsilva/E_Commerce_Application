from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from pydantic import BaseModel, Field
from typing import Optional

cat_router = APIRouter(prefix="/categories", tags=["Categories"])

@cat_router.get("/")
def list_categories(db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT id, category FROM categories")
        return cursor.fetchall()

@cat_router.post("/")
def add_category(body: dict, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT id FROM categories WHERE id = %s", (body["id"],))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Category ID already exists")
        cursor.execute(
            "INSERT INTO categories (id, category) VALUES (%s, %s)",
            (body["id"], body["category"])
        )
    return {"id": body["id"], "category": body["category"]}


router = APIRouter(prefix="/products", tags=["Products and Inventory"])

class ProductCreate(BaseModel):
    product_name: str
    brand: str
    price: float = Field(ge=0)
    category: int
    description: str
    quantity: int = Field(ge=0, default=0)
    image: Optional[str] = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80"

class ProductUpdate(BaseModel):
    product_name: str
    brand: str
    price: float = Field(ge=0)
    category: int
    description: str
    image: Optional[str] = None

class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)

class StockDeduct(BaseModel):
    quantity: int = Field(gt=0)


@router.get("/")
def list_all_products(db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.p_id,
                p.product_name,
                p.brand,
                p.price,
                p.category,
                c.category  AS category_name,
                p.description,
                p.image,
                i.quantity  AS stock,
                i.last_updated,
                CASE WHEN i.quantity > 0 THEN 'In Stock' ELSE 'Out of Stock' END AS stock_status
            FROM Products p
            JOIN Inventory i ON p.p_id = i.p_id
            JOIN categories c ON p.category = c.id
            WHERE p.is_active = 1
            ORDER BY i.quantity DESC
        """)
        return cursor.fetchall()


@router.get("/{p_id}")
def get_product(p_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.p_id,
                p.product_name,
                p.brand,
                p.price,
                p.category,
                c.category  AS category_name,
                p.description,
                p.image,
                i.quantity  AS stock,
                i.last_updated,
                CASE WHEN i.quantity > 0 THEN 'In Stock' ELSE 'Out of Stock' END AS stock_status
            FROM Products p
            JOIN Inventory i ON p.p_id = i.p_id
            JOIN categories c ON p.category = c.id
            WHERE p.p_id = %s
        """, (p_id,))
        product = cursor.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/")
def create_product(product: ProductCreate, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT MAX(p_id) AS max_id FROM Products")
        row = cursor.fetchone()
        new_id = (row["max_id"] or 0) + 1

        cursor.execute("""
            INSERT INTO Products
                (p_id, product_name, brand, price, category, description, image, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """, (new_id, product.product_name, product.brand,
              product.price, product.category, product.description, product.image))

        if product.quantity > 0:
            cursor.execute(
                "UPDATE Inventory SET quantity = %s WHERE p_id = %s",
                (product.quantity, new_id)
            )
    return {"message": "Product created", "p_id": new_id}


@router.put("/{p_id}")
def update_product(p_id: int, body: ProductUpdate, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            UPDATE Products
            SET product_name=%s, brand=%s, price=%s, category=%s, description=%s, image=%s
            WHERE p_id=%s
        """, (body.product_name, body.brand, body.price,
              body.category, body.description, body.image, p_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated", "p_id": p_id}


@router.delete("/{p_id}")
def delete_product(p_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE Products SET is_active = 0 WHERE p_id = %s", (p_id,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product removed from catalog", "p_id": p_id}


@router.put("/{p_id}/inventory")
def update_stock(p_id: int, body: InventoryUpdate, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE Inventory SET quantity = %s WHERE p_id = %s",
            (body.quantity, p_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Stock updated", "p_id": p_id, "new_quantity": body.quantity}


@router.post("/{p_id}/deduct")
def deduct_product_stock(p_id: int, body: StockDeduct, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("CALL deduct_stock(%s, %s)", (p_id, body.quantity))
        cursor.execute(
            "SELECT quantity FROM Inventory WHERE p_id = %s", (p_id,)
        )
        row = cursor.fetchone()
    return {"message": "Stock deducted", "p_id": p_id, "remaining": row["quantity"]}