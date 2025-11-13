from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
import database


router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)

# Dependencia para obtener la sesión de DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST /carts
@router.post("/", response_model=schemas.Cart, status_code=201)
def create_cart(cart: schemas.CartCreate, db: Session = Depends(get_db)):
    # Validar que los productos existen y hay stock suficiente
    for item in cart.items:
        product = crud.get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        if item.qty > product.cantidad_disponible:
            raise HTTPException(status_code=400, detail=f"No hay suficiente stock para {product.tipo_prenda} ({product.talla})")
    
    new_cart = crud.create_cart(db, cart)
    return new_cart

# PATCH /carts/{id}
@router.patch("/{cart_id}", response_model=schemas.Cart)
def update_cart(cart_id: int, cart_update: schemas.CartCreate, db: Session = Depends(get_db)):
    # Validar productos
    for item in cart_update.items:
        product = crud.get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        if item.qty > product.cantidad_disponible:
            raise HTTPException(status_code=400, detail=f"No hay suficiente stock para {product.tipo_prenda} ({product.talla})")
    
    updated_cart = crud.update_cart(db, cart_id, cart_update)
    if not updated_cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return updated_cart

# GET /carts -> listar todos los carritos
@router.get("/", response_model=List[schemas.Cart])
def get_carts(db: Session = Depends(get_db)):
    return crud.get_all_carts(db)

# GET /carts/{cart_id} -> obtener carrito por ID
@router.get("/{cart_id}", response_model=schemas.Cart)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = crud.get_cart(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return cart
