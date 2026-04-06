from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Category(Base):
    __tablename__ = "categories"
    id       = Column(Integer, primary_key=True)
    category = Column(String(255), nullable=False)

class Product(Base):
    __tablename__ = "Products"
    p_id         = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    brand        = Column(String(255), nullable=False)
    price        = Column(Float, nullable=False)
    category     = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description  = Column(Text, nullable=False)
    is_active    = Column(SmallInteger, default=1, nullable=False)

    inventory     = relationship("Inventory", back_populates="product", uselist=False)
    category_info = relationship("Category")

class Inventory(Base):
    __tablename__ = "Inventory"
    p_id         = Column(Integer, ForeignKey("Products.p_id"), primary_key=True)
    quantity     = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="inventory")