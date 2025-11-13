from fastapi import FastAPI
from routers import products, carts
from database import engine, Base

# Crear todas las tablas definidas en models.py (si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Laburen Store API",
    description="API para manejar productos y carritos de compra",
    version="1.0.0"
)

# Incluir routers
app.include_router(products.router)
app.include_router(carts.router)

# Endpoint raíz opcional
@app.get("/")
def read_root():
    return {"message": "Bienvenido a Laburen Store API"}
