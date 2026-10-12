"""Junta todas las rutas en un solo lugar (equivale a urls.py en Django)."""
from fastapi import APIRouter

from app.api.rutas import (alertas, asistente, auth, dispositivos, educacion, lecturas, perfil, privacidad,
                           recordatorios, reportes)

api_router = APIRouter()
for modulo in (auth, perfil, dispositivos, lecturas, alertas, recordatorios, reportes, educacion,
               asistente, privacidad):
    api_router.include_router(modulo.router)
