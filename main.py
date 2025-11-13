from fastapi import FastAPI
from routers import products, carts
from database import engine, Base
import load_products  

Base.metadata.create_all(bind=engine)

try:
    load_products.main()  # asegurate que tu script tenga una función main()
    print("Products loaded successfully.")
except Exception as e:
    print(f"Error loading products: {e}")

app = FastAPI(
    title="Laburen Store API",
    description="API para manejar productos y carritos de compra",
    version="1.0.0"
)

app.include_router(products.router)
app.include_router(carts.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a Laburen Store API"}
