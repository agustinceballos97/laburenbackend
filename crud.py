from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
import models
import schemas
# 🚨 Importamos func para poder usar group_by
from sqlalchemy import func 


def get_products(db: Session, skip: int = 0, limit: int = 100, q: str = None):
    """
    Obtiene una lista de productos, aplicando un filtro de búsqueda 'q'.
    Se corrige la duplicación de IDs usando group_by.
    """
    query = db.query(models.Product)

    if q:
        keywords = q.lower().split()
        for kw in keywords:
            query = query.filter(
                or_(
                    models.Product.tipo_prenda.ilike(f"%{kw}%"),
                    models.Product.color.ilike(f"%{kw}%"),
                    models.Product.talla.ilike(f"%{kw}%"),
                    models.Product.descripcion.ilike(f"%{kw}%"),
                    models.Product.categoria.ilike(f"%{kw}%")
                )
            )
    
    # 🌟 CORRECCIÓN para evitar duplicación de IDs 🌟
    # Usar .group_by(models.Product.id) fuerza a que cada ID sea devuelto una sola vez.
    return query.group_by(models.Product.id).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    """Obtiene un producto por ID."""
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def create_cart(db: Session, cart: schemas.CartCreate):
    """Crea un carrito y sus items."""
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
    """Actualiza un carrito existente (reemplaza todos los ítems)."""
    db_cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not db_cart:
        return None

    # Eliminar ítems previos
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).delete()
    db.commit()

    # Agregar nuevos ítems
    for item in cart_update.items:
        db_item = models.CartItem(cart_id=cart_id, product_id=item.product_id, qty=item.qty)
        db.add(db_item)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def get_all_carts(db: Session, q: str = None):
    """
    Lista todos los carritos.
    Si se pasa 'q', busca por ID de carrito o por nombre de producto dentro del carrito.
    """
    query = db.query(models.Cart).options(joinedload(models.Cart.items).joinedload(models.CartItem.product))

    if q:
        # Si q es numérico, intenta filtrar por ID exacto
        if q.isdigit():
            query = query.filter(models.Cart.id == int(q))
        else:
            # Buscar por nombre o tipo de producto dentro del carrito
            query = query.join(models.Cart.items).join(models.CartItem.product).filter(
                or_(
                    models.Product.tipo_prenda.ilike(f"%{q}%"),
                    models.Product.color.ilike(f"%{q}%"),
                    models.Product.descripcion.ilike(f"%{q}%")
                )
            ).distinct()

    return query.all()


def get_cart(db: Session, cart_id: int):
    """Obtiene un carrito con sus productos."""
    return (
        db.query(models.Cart)
        .options(joinedload(models.Cart.items).joinedload(models.CartItem.product))
        .filter(models.Cart.id == cart_id)
        .first()
    )
