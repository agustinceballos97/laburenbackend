from fastapi import FastAPI

app = FastAPI(title="Backend Vacío Laburen")

@app.get("/")
def read_root():
    return {"message": "Backend FastAPI desplegado correctamente!"}