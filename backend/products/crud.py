from sqlalchemy.orm import Session
from . import models, schemas

def _format(p):
    qty = p.inventory.quantity if p.inventory else 0
    return {
        "p_id":         p.p_id,
        "product_name": p.product_name,
        "brand":        p.brand,
        "price":        p.price,
        "category":     p.category,
        "description":  p.description,
        "is_active":    p.is_active,
        "quantity":     qty,
        "stock_status": "In Stock" if qty > 0 else "Out of Stock",
        "last_updated": (
            p.inventory.last_updated.isoformat()
            if p.inventory and p.inventory.last_updated else None
        ),
    }

def get_all_products(db: Session):
    # Only return active products, in stock first
    products = db.query(models.Product).filter(
        models.Product.is_active == 1
    ).all()

    in_stock     = [_format(p) for p in products if p.inventory and p.inventory.quantity > 0]
    out_of_stock = [_format(p) for p in products if not p.inventory or p.inventory.quantity == 0]
    return in_stock + out_of_stock

def get_product_by_id(db: Session, p_id: int):
    p = db.query(models.Product).filter(models.Product.p_id == p_id).first()
    if not p:
        return None
    return _format(p)

def add_product(db: Session, product: schemas.ProductCreate):
    max_id = db.query(models.Product).count()
    new_id = max_id + 1
    while db.query(models.Product).filter(models.Product.p_id == new_id).first():
        new_id += 1

    db_product = models.Product(
        p_id=new_id,
        product_name=product.product_name,
        brand=product.brand,
        price=product.price,
        category=product.category,
        description=product.description,
        is_active=1,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Trigger already created the inventory row.
    # Now just update the quantity if > 0
    if product.quantity > 0:
        inv = db.query(models.Inventory).filter(
            models.Inventory.p_id == new_id
        ).first()
        if inv:
            inv.quantity = product.quantity
            db.commit()

    return db_product

def update_product(db: Session, p_id: int, data: schemas.ProductUpdate):
    p = db.query(models.Product).filter(models.Product.p_id == p_id).first()
    if not p:
        return None
    p.product_name = data.product_name
    p.brand        = data.brand
    p.price        = data.price
    p.category     = data.category
    p.description  = data.description
    db.commit()
    db.refresh(p)
    return p

def soft_delete_product(db: Session, p_id: int):
    """
    Soft delete — hides product from catalog.
    All order history is preserved in ordered_items.
    """
    p = db.query(models.Product).filter(models.Product.p_id == p_id).first()
    if not p:
        return None
    p.is_active = 0
    db.commit()
    return p

def update_inventory(db: Session, p_id: int, quantity: int):
    inv = db.query(models.Inventory).filter(
        models.Inventory.p_id == p_id
    ).first()
    if not inv:
        return None
    inv.quantity = quantity
    db.commit()
    db.refresh(inv)
    return inv

def deduct_stock(db: Session, p_id: int, qty: int):
    inv = db.query(models.Inventory)\
            .filter(models.Inventory.p_id == p_id)\
            .with_for_update()\
            .first()
    if not inv:
        raise ValueError(f"Product {p_id} not found")
    if inv.quantity < qty:
        raise ValueError(f"Insufficient stock for product {p_id}")
    inv.quantity -= qty
    db.commit()
    return inv