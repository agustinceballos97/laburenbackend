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
        or_filters = []

        # Construimos un solo OR con todas las palabras y campos
        for kw in keywords:
            or_filters.extend([
                models.Product.tipo_prenda.ilike(f"%{kw}%"),
                models.Product.color.ilike(f"%{kw}%"),
                models.Product.talla.ilike(f"%{kw}%"),
                models.Product.descripcion.ilike(f"%{kw}%"),
                models.Product.categoria.ilike(f"%{kw}%"),
            ])

        query = query.filter(or_(*or_filters))

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    """
    Trae un producto por su ID.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()


# -------------------------------
# CARRITO
# -------------------------------

def create_cart(db: Session, cart: schemas.CartCreate):
    """
    Crea un carrito y sus items.
    """
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
    """
    Actualiza un carrito existente reemplazando sus items.
    """
    db_cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not db_cart:
        return None

    # Borramos los items anteriores
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).delete()
    db.commit()

    # Agregamos los nuevos items
    for item in cart_update.items:
        db_item = models.CartItem(cart_id=cart_id, product_id=item.product_id, qty=item.qty)
        db.add(db_item)

    db.commit()
    db.refresh(db_cart)
    return db_cart


def get_all_carts(db: Session, q: str = None):
    """
    Trae todos los carritos.
    Si se pasa 'q', filtra por productos dentro de los carritos.
    """
    query = db.query(models.Cart)

    if q:
        if q.isdigit():
            query = query.filter(models.Cart.id == int(q))
        else:
            # filtramos carritos por productos que coinciden con q
            keywords = q.lower().split()
            or_filters = []
            for kw in keywords:
                or_filters.extend([
                    models.Product.tipo_prenda.ilike(f"%{kw}%"),
                    models.Product.color.ilike(f"%{kw}%"),
                    models.Product.talla.ilike(f"%{kw}%"),
                    models.Product.descripcion.ilike(f"%{kw}%"),
                    models.Product.categoria.ilike(f"%{kw}%"),
                ])

            query = query.join(models.Cart.items).join(models.CartItem.product)
            query = query.filter(or_(*or_filters)).distinct()

    return query.all()


def get_cart(db: Session, cart_id: int):
    """
    Trae un carrito específico por ID.
    """
    return db.query(models.Cart).filter(models.Cart.id == cart_id).first()
