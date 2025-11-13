from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    tipo_prenda: str
    talla: str
    color: str
    cantidad_disponible: int
    precio_50_u: float
    precio_100_u: float
    precio_200_u: float
    disponible: bool
    categoria: str
    descripcion: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True

class CartItemBase(BaseModel):
    product_id: int
    qty: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    product: Product
    class Config:
        orm_mode = True

class CartBase(BaseModel):
    pass

class CartCreate(BaseModel):
    items: List[CartItemCreate]

class Cart(CartBase):
    id: int
    items: List[CartItem] = []
    class Config:
        orm_mode = True
