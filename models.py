from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tipo_prenda = Column(String, nullable=False)
    talla = Column(String, nullable=False)
    color = Column(String, nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)
    precio_50_u = Column(Float, nullable=False)
    precio_100_u = Column(Float, nullable=False)
    precio_200_u = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)
    categoria = Column(String, nullable=False)
    descripcion = Column(Text)

    cart_items = relationship("CartItem", back_populates="product")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
