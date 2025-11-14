from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
import schemas

# -------------------------------
# PRODUCTOS
# -------------------------------

def get_products(db: Session, skip: int = 0, limit: int = 100, q: str = None):
    """
    Trae productos filtrando por keywords, sin duplicar.
    """
    query = db.query(models.Product)

    if q:
        keywords = q.lower().split()
        # Para cada keyword, buscamos en todos los campos relevantes
        or_filters = [
            or_(
                models.Product.tipo_prenda.ilike(f"%{kw}%"),
                models.Product.color.ilike(f"%{kw}%"),
                models.Product.talla.ilike(f"%{kw}%"),
                models.Product.descripcion.ilike(f"%{kw}%"),
                models.Product.categoria.ilike(f"%{kw}%"),
            )
            for kw in keywords
        ]
        # Aplicamos todos los ORs como filtros independientes (cada palabra puede estar en cualquier campo)
        query = query.filter(*or_filters)

    # Aseguramos que cada producto aparezca solo una vez
    query = query.distinct(models.Product.id)

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    """
    Trae un producto por su ID.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def create_product(db: Session, product: schemas.ProductCreate):
    """
    Crea un producto nuevo.
    """
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    """
    Actualiza un producto existente.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None

    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    """
    Borra un producto por ID.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None

    db.delete(db_product)
    db.commit()
    return db_product
