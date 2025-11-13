from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import models
import schemas
import database

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# Dependencia para obtener la sesión de DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET /products?q=
@router.get("/", response_model=List[schemas.Product])
def list_products(q: Optional[str] = Query(None, description="Filtro por nombre o descripción"),
                  db: Session = Depends(get_db)):
    products = crud.get_products(db, q=q)
    return products

# GET /products/{id}
@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product
