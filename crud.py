from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
import models
import schemas

# -------------------------------
# Productos
# -------------------------------

def get_products(db: Session, skip: int = 0, limit: int = 100, q: str = None):
    """
    Trae productos filtrando por keywords sin duplicar.
    Las relaciones se cargan con selectinload para no multiplicar filas.
    """
    query = db.query(models.Product).options(selectinload(models.Product.categorias))  # cargar relaciones sin duplicar

    if q:
        keywords = q.lower().split()
        for kw in keywords:
            query = query.filter(
                or_(
                    models.Product.tipo_prenda.ilike(f"%{kw}%"),
                    models.Product.color.ilike(f"%{kw}%"),
                    models.Product.talla.ilike(f"%{kw}%"),
                    models.Product.descripcion.ilike(f"%{kw}%"),
                    models.Product.categoria.ilike(f"%{kw}%"),
                )
            )

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(models.Product).options(selectinload(models.Product.categorias)).filter(
        models.Product.id == product_id
    ).first()


# -------------------------------
# Carrito
# -------------------------------

def create_cart(db: Session, cart: schemas.CartCreate):
    db_cart = models.Cart()
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)

    for item in cart.items:
        db_item = models.CartItem(cart_id=db_cart.id, product_id=item.product_id, qty=item.qty)
        db.add(db_item)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def update_cart(db: Session, cart_id: int, cart_update: schemas.CartCreate):
    db_cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not db_cart:
        return None

    db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).delete()
    db.commit()

    for item in cart_update.items:
        db_item = models.CartItem(cart_id=cart_id, product_id=item.product_id, qty=item.qty)
        db.add(db_item)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def get_all_carts(db: Session, q: str = None):
    """
    Devuelve todos los carritos, filtrando por productos si q está presente.
    Las relaciones se cargan con selectinload para evitar duplicados.
    """
    query = db.query(models.Cart).options(
        selectinload(models.Cart.items).selectinload(models.CartItem.product)
    )

    if q:
        if q.isdigit():
            query = query.filter(models.Cart.id == int(q))
        else:
            query = query.join(models.Cart.items).join(models.CartItem.product).filter(
                or_(
                    models.Product.tipo_prenda.ilike(f"%{q}%"),
                    models.Product.color.ilike(f"%{q}%"),
                    models.Product.descripcion.ilike(f"%{q}%")
                )
            ).distinct()

    return query.all()


def get_cart(db: Session, cart_id: int):
    return db.query(models.Cart).options(
        selectinload(models.Cart.items).selectinload(models.CartItem.product)
    ).filter(models.Cart.id == cart_id).first()
