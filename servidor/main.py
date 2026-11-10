from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from servidor.base_datos import Base, engine
from servidor.config import CARPETA_UPLOADS
import servidor.modelos  # noqa: F401  (registra los modelos)
from servidor.rutas import auth, vehiculos

app = FastAPI(title="Autos App API")

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# Crea la carpeta de imagenes y la expone como /uploads/<archivo>
CARPETA_UPLOADS.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=CARPETA_UPLOADS), name="uploads")

app.include_router(auth.router)
app.include_router(vehiculos.router)


@app.get("/")
def raiz():
    return {"mensaje": "API funcionando"}