"""PUNTO DE ENTRADA del backend.

Para encenderlo (desde la carpeta backend/):
    uvicorn app.main:app --reload

Luego abra http://127.0.0.1:8000/docs para ver y probar todas las rutas.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.inicializar import crear_tablas

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    crear_tablas()   # al arrancar: crea las tablas si no existen
    yield


app = FastAPI(
    title=settings.nombre_app,
    version="1.0.0",
    description="API para el monitoreo y control de la hipertensión arterial.",
    lifespan=ciclo_de_vida,
)

# CORS: permite que el frontend (que vive en otra dirección) llame a esta API.
app.add_middleware(CORSMiddleware, allow_origins=settings.lista_cors, allow_methods=["*"], allow_headers=["*"])

app.include_router(api_router)


@app.get("/", tags=["Estado"])
def estado():
    """Sirve para comprobar que el servidor está encendido."""
    return {"servicio": settings.nombre_app, "estado": "ok", "documentacion": "/docs"}
