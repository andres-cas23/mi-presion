"""/recordatorios: medición, medicamentos y citas (RF-06)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_propio, usuario_actual
from app.core.tiempo import ahora
from app.db.sesion import obtener_db
from app.models import Recordatorio, Usuario
from app.schemas import RecordatorioEntrada, RecordatorioProximo, RecordatorioSalida
from app.services.recordatorios import proximas_ocurrencias

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])


@router.get("", response_model=list[RecordatorioSalida])
def listar(u: Usuario = Depends(usuario_actual)):
    return [r for r in u.recordatorios if r.activo]


@router.post("", response_model=RecordatorioSalida, status_code=201)
def crear(datos: RecordatorioEntrada, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    r = Recordatorio(usuario_id=u.id, tipo=datos.tipo.value, titulo=datos.titulo, hora=datos.hora,
                     dias_semana=datos.dias_semana, fecha=datos.fecha)
    db.add(r)
    db.commit()
    return r


@router.delete("/{rec_id}", status_code=204)
def desactivar(rec_id: int, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    obtener_propio(db, Recordatorio, rec_id, u, "Recordatorio").activo = False
    db.commit()


@router.get("/proximos", response_model=list[RecordatorioProximo])
def proximos(horas: int = Query(24, ge=1, le=24 * 14), u: Usuario = Depends(usuario_actual)):
    return [RecordatorioProximo(recordatorio=RecordatorioSalida.model_validate(r), programado_para=t)
            for r, t in proximas_ocurrencias(u.recordatorios, ahora(), horas)]
