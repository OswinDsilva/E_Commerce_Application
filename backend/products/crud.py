from pymysql.connections import Connection

def _format(p):
    """Format product row as response"""
    qty = p.get('quantity', 0) if p.get('quantity') else 0
    return {
        "p_id": p['p_id'],
        "product_name": p['product_name'],
        "brand": p['brand'],
        "price": float(p['price']),
        "category": p['category'],
        "description": p['description'],
        "is_active": p['is_active'],
        "quantity": qty,
        "stock_status": "In Stock" if qty > 0 else "Out of Stock",
        "last_updated": str(p.get('last_updated')) if p.get('last_updated') else None,
    }

def get_all_products(db: Connection):
    """Get all active products, in-stock first"""
    with db.cursor() as cursor:
        query = """
            SELECT p.p_id, p.product_name, p.brand, p.price, p.category, 
                   p.description, p.is_active, i.quantity, i.last_updated
            FROM Products p
            LEFT JOIN Inventory i ON p.p_id = i.p_id
            WHERE p.is_active = 1
            ORDER BY (i.quantity > 0) DESC, p.p_id
        """
        cursor.execute(query)
        results = cursor.fetchall()
    return [_format(p) for p in results] if results else []

def get_product_by_id(db: Connection, p_id: int):
    """Get single product by ID"""
    with db.cursor() as cursor:
        query = """
            SELECT p.p_id, p.product_name, p.brand, p.price, p.category,
                   p.description, p.is_active, i.quantity, i.last_updated
            FROM Products p
            LEFT JOIN Inventory i ON p.p_id = i.p_id
            WHERE p.p_id = %s AND p.is_active = 1
        """
        cursor.execute(query, (p_id,))
        result = cursor.fetchone()
    if not result:
        return None
    return _format(result)

def add_product(db: Connection, product):
    """Add new product with inventory"""
    with db.cursor() as cursor:
        try:
            insert_product = """
                INSERT INTO Products (product_name, brand, price, category, description, is_active)
                VALUES (%s, %s, %s, %s, %s, 1)
            """
            cursor.execute(insert_product, (
                product.product_name, product.brand, product.price,
                product.category, product.description
            ))
            db.commit()
            
            cursor.execute("SELECT LAST_INSERT_ID() as p_id")
            new_id = cursor.fetchone()['p_id']
            
            if product.quantity > 0:
                insert_inv = """
                    INSERT INTO Inventory (p_id, quantity)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_inv, (new_id, product.quantity))
                db.commit()
            
            return get_product_by_id(db, new_id)
        except Exception as e:
            db.rollback()
            raise

def update_product(db: Connection, p_id: int, data):
    """Update product details"""
    with db.cursor() as cursor:
        try:
            cursor.execute("SELECT p_id FROM Products WHERE p_id = %s", (p_id,))
            if not cursor.fetchone():
                return None
            
            update_query = """
                UPDATE Products
                SET product_name = %s, brand = %s, price = %s, 
                    category = %s, description = %s
                WHERE p_id = %s
            """
            cursor.execute(update_query, (
                data.product_name, data.brand, data.price,
                data.category, data.description, p_id
            ))
            db.commit()
            return get_product_by_id(db, p_id)
        except Exception as e:
            db.rollback()
            raise

def soft_delete_product(db: Connection, p_id: int):
    """Soft delete - hide product from catalog"""
    with db.cursor() as cursor:
        try:
            cursor.execute("SELECT p_id FROM Products WHERE p_id = %s", (p_id,))
            if not cursor.fetchone():
                return None
            
            cursor.execute("UPDATE Products SET is_active = 0 WHERE p_id = %s", (p_id,))
            db.commit()
            return {"message": "deleted", "p_id": p_id}
        except Exception as e:
            db.rollback()
            raise

def update_inventory(db: Connection, p_id: int, quantity: int):
    """Update product inventory quantity"""
    with db.cursor() as cursor:
        try:
            cursor.execute("SELECT p_id FROM Products WHERE p_id = %s", (p_id,))
            if not cursor.fetchone():
                return None
            
            cursor.execute("SELECT p_id FROM Inventory WHERE p_id = %s", (p_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE Inventory SET quantity = %s WHERE p_id = %s", (quantity, p_id))
            else:
                cursor.execute("INSERT INTO Inventory (p_id, quantity) VALUES (%s, %s)", (p_id, quantity))
            
            db.commit()
            return get_product_by_id(db, p_id)
        except Exception as e:
            db.rollback()
            raise

def deduct_stock(db: Connection, p_id: int, quantity: int):
    """Deduct stock from product inventory"""
    with db.cursor() as cursor:
        try:
            cursor.execute("SELECT quantity FROM Inventory WHERE p_id = %s", (p_id,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError("Product not found in inventory")
            
            current_qty = result['quantity']
            if current_qty < quantity:
                raise ValueError(f"Insufficient stock. Available: {current_qty}, Requested: {quantity}")
            
            new_qty = current_qty - quantity
            cursor.execute("UPDATE Inventory SET quantity = %s WHERE p_id = %s", (new_qty, p_id))
            db.commit()
            
            product = get_product_by_id(db, p_id)
            return product if product else {"quantity": new_qty}
        except Exception as e:
            db.rollback()
            raise

def get_all_categories(db: Connection):
    """Get all product categories"""
    with db.cursor() as cursor:
        cursor.execute("SELECT id, category FROM categories ORDER BY id")
        results = cursor.fetchall()
    return results if results else []

def add_category(db: Connection, category_name: str):
    """Add new category"""
    with db.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO categories (category) VALUES (%s)", (category_name,))
            db.commit()
            cursor.execute("SELECT LAST_INSERT_ID() as id")
            new_id = cursor.fetchone()['id']
            return {"id": new_id, "category": category_name}
        except Exception as e:
            db.rollback()
            raise