import os
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

def load_products_from_excel(file_path: str):
    df = pd.read_excel(file_path)

    db: Session = SessionLocal()

    try:
        for _, row in df.iterrows():
            product = models.Product(
                tipo_prenda=row["TIPO_PRENDA"],
                talla=row["TALLA"],
                color=row["COLOR"],
                cantidad_disponible=int(row["CANTIDAD_DISPONIBLE"]),
                precio_50_u=float(row["PRECIO_50_U"]),
                precio_100_u=float(row["PRECIO_100_U"]),
                precio_200_u=float(row["PRECIO_200_U"]),
                disponible=True if str(row["DISPONIBLE"]).strip().lower() in ["si", "sí", "true", "1"] else False,
                categoria=row["CATEGORÍA"],
                descripcion=row["DESCRIPCIÓN"]
            )
            db.add(product)

        db.commit()
        print(f"✅ Se cargaron {len(df)} productos correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al cargar productos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Path al archivo Excel (desde dentro del contenedor)
    file_path = "/app/app/products.xlsx"
    if not os.path.exists(file_path):
        print(f"❌ No se encontró el archivo: {file_path}")
    else:
        load_products_from_excel(file_path)
