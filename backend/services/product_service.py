from datetime import datetime
from decimal import Decimal
from typing import Any

from ..errors import ApiError
from ..schemas.products import (
    CategoryOut,
    ProductCreateRequest,
    ProductOut,
    ProductUpdateRequest,
)
from .common import get_next_id


def _to_product_out(row: dict[str, Any]) -> ProductOut:
    quantity = int(row.get("quantity") or 0)
    thumbnail_url = row.get("thumbnail_url")
    return ProductOut.model_validate(
        {
            "p_id": row["p_id"],
            "product_name": row["product_name"],
            "brand": row["brand"],
            "price": row["price"] if isinstance(row["price"], Decimal) else Decimal(str(row["price"])),
            "category_id": row["category_id"],
            "category_name": row.get("category_name"),
            "description": row["description"],
            "thumbnail_url": thumbnail_url,
            "image": thumbnail_url,
            "quantity": quantity,
            "stock_status": "In Stock" if quantity > 0 else "Out of Stock",
            "last_updated": row.get("last_updated"),
        }
    )


def _fetch_product_row(connection: Any, p_id: int) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                p.p_id,
                p.product_name,
                p.brand,
                p.price,
                p.category_id,
                c.category AS category_name,
                p.description,
                p.thumbnail_url,
                i.quantity,
                i.last_updated
            FROM Products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN Inventory i ON i.p_id = p.p_id
            WHERE p.p_id = %s
            LIMIT 1
            """,
            (p_id,),
        )
        return cursor.fetchone()


def list_products(connection: Any) -> list[ProductOut]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                p.p_id,
                p.product_name,
                p.brand,
                p.price,
                p.category_id,
                c.category AS category_name,
                p.description,
                p.thumbnail_url,
                i.quantity,
                i.last_updated
            FROM Products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN Inventory i ON i.p_id = p.p_id
            ORDER BY COALESCE(i.quantity, 0) DESC, p.p_id
            """
        )
        rows = cursor.fetchall()

    return [_to_product_out(row) for row in rows]


def get_product_by_id(connection: Any, p_id: int) -> ProductOut | None:
    row = _fetch_product_row(connection, int(p_id))
    if not row:
        return None
    return _to_product_out(row)


def _validate_category_exists(connection: Any, category_id: int) -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM categories WHERE id = %s LIMIT 1", (category_id,))
        if not cursor.fetchone():
            raise ApiError("Category not found", "NOT_FOUND", 404)


def create_product(connection: Any, payload: ProductCreateRequest) -> ProductOut:
    _validate_category_exists(connection, payload.category_id)
    p_id = get_next_id(connection, "Products", "p_id")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Products (p_id, product_name, brand, price, category_id, description, thumbnail_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                p_id,
                payload.product_name,
                payload.brand,
                payload.price,
                payload.category_id,
                payload.description,
                payload.thumbnail_url,
            ),
        )

        cursor.execute(
            """
            INSERT INTO Inventory (p_id, quantity, last_updated)
            VALUES (%s, %s, %s)
            """,
            (p_id, payload.quantity, datetime.utcnow()),
        )

    created = get_product_by_id(connection, p_id)
    if not created:
        raise ApiError("Unable to create product", "SERVER_ERROR", 500)

    return created


def update_product(connection: Any, p_id: int, payload: ProductUpdateRequest) -> ProductOut | None:
    existing = get_product_by_id(connection, p_id)
    if not existing:
        return None

    _validate_category_exists(connection, payload.category_id)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE Products
            SET product_name = %s,
                brand = %s,
                price = %s,
                category_id = %s,
                description = %s,
                thumbnail_url = COALESCE(%s, thumbnail_url)
            WHERE p_id = %s
            """,
            (
                payload.product_name,
                payload.brand,
                payload.price,
                payload.category_id,
                payload.description,
                payload.thumbnail_url,
                p_id,
            ),
        )

    return get_product_by_id(connection, p_id)


def delete_product(connection: Any, p_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT p_id FROM Products WHERE p_id = %s LIMIT 1", (p_id,))
        if not cursor.fetchone():
            return False

        cursor.execute("SELECT 1 FROM ordered_items WHERE p_id = %s LIMIT 1", (p_id,))
        if cursor.fetchone():
            raise ApiError(
                "Cannot delete product with existing order history",
                "BAD_REQUEST",
                400,
            )

        cursor.execute("DELETE FROM Products WHERE p_id = %s", (p_id,))

    return True


def update_inventory(connection: Any, p_id: int, quantity: int) -> ProductOut | None:
    existing = get_product_by_id(connection, p_id)
    if not existing:
        return None

    with connection.cursor() as cursor:
        cursor.execute("SELECT p_id FROM Inventory WHERE p_id = %s LIMIT 1", (p_id,))
        if cursor.fetchone():
            cursor.execute(
                """
                UPDATE Inventory
                SET quantity = %s,
                    last_updated = %s
                WHERE p_id = %s
                """,
                (quantity, datetime.utcnow(), p_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO Inventory (p_id, quantity, last_updated)
                VALUES (%s, %s, %s)
                """,
                (p_id, quantity, datetime.utcnow()),
            )

    return get_product_by_id(connection, p_id)


def deduct_stock(connection: Any, p_id: int, quantity: int) -> ProductOut:
    with connection.cursor() as cursor:
        cursor.execute("SELECT quantity FROM Inventory WHERE p_id = %s LIMIT 1", (p_id,))
        row = cursor.fetchone()

    if not row:
        raise ApiError("Product inventory not found", "NOT_FOUND", 404)

    current_quantity = int(row.get("quantity") or 0)
    if current_quantity < quantity:
        raise ApiError(
            f"Insufficient stock. Available: {current_quantity}, requested: {quantity}",
            "BAD_REQUEST",
            400,
        )

    updated = update_inventory(connection, p_id, current_quantity - quantity)
    if not updated:
        raise ApiError("Product not found", "NOT_FOUND", 404)

    return updated


def list_categories(connection: Any) -> list[CategoryOut]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, category FROM categories ORDER BY id")
        rows = cursor.fetchall()

    return [CategoryOut.model_validate(row) for row in rows]


def create_category(connection: Any, category: str) -> CategoryOut:
    category_name = category.strip()
    if not category_name:
        raise ApiError("category is required", "BAD_REQUEST", 400)

    category_id = get_next_id(connection, "categories", "id")
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO categories (id, category) VALUES (%s, %s)",
            (category_id, category_name),
        )

    return CategoryOut(id=category_id, category=category_name)
