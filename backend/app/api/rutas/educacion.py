"""/educacion: contenido educativo, público (RF-08)."""
from fastapi import APIRouter, HTTPException

from app.services import educacion

router = APIRouter(prefix="/educacion", tags=["Educación"])


@router.get("")
def listar():
    return educacion.listar()


@router.get("/{slug}")
def ver(slug: str):
    item = educacion.obtener(slug)
    if not item:
        raise HTTPException(404, "Contenido no encontrado")
    return item
