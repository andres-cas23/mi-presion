"""/alertas: avisos de presión muy alta o muy baja (RF-05)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_propio, usuario_actual
from app.db.sesion import obtener_db
from app.models import Alerta, Usuario
from app.schemas import AlertaSalida

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("", response_model=list[AlertaSalida])
def listar(solo_pendientes: bool = True, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    q = select(Alerta).where(Alerta.usuario_id == u.id)
    if solo_pendientes:
        q = q.where(Alerta.atendida.is_(False))
    return list(db.scalars(q.order_by(Alerta.creada_en.desc())))


@router.post("/{alerta_id}/atender", response_model=AlertaSalida)
def atender(alerta_id: int, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    a = obtener_propio(db, Alerta, alerta_id, u, "Alerta")
    a.atendida = True
    db.commit()
    return a
