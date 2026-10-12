"""/lecturas: mediciones, protocolo de casa (HBPM) y tendencias (RF-02/03/04/09)."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_propio, usuario_actual
from app.core.tiempo import ahora
from app.db.sesion import obtener_db
from app.models import Dispositivo, Lectura, Usuario
from app.models.enums import Fuente
from app.schemas import (AlertaSalida, LecturaEntrada, LecturaSalida, ResultadoRegistro,
                         ResultadoSincronizacion, SincronizacionLote)
from app.services.hbpm import resumen_hbpm, tendencias
from app.services.lecturas import consultar_lecturas, registrar_lectura

router = APIRouter(prefix="/lecturas", tags=["Lecturas"])


@router.get("", response_model=list[LecturaSalida])
def listar(desde: datetime | None = None, hasta: datetime | None = None,
           u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    return consultar_lecturas(db, u.id, desde, hasta)


@router.post("/manual", response_model=ResultadoRegistro, status_code=201)
def registrar_manual(datos: LecturaEntrada, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    """Registro manual de respaldo (RF-09). Sigue la misma ruta que la sincronización."""
    r = registrar_lectura(db, u, datos, Fuente.MANUAL)
    return ResultadoRegistro(lectura=LecturaSalida.model_validate(r.lectura),
                             alerta=AlertaSalida.model_validate(r.alerta) if r.alerta else None,
                             mensaje=r.mensaje, duplicada=r.duplicada)


@router.post("/sincronizar", response_model=ResultadoSincronizacion)
def sincronizar_lote(datos: SincronizacionLote, u: Usuario = Depends(usuario_actual),
                     db: Session = Depends(obtener_db)):
    """Lote desde Apple Health / Google Fit / Samsung Health. No duplica gracias a `id_externo`."""
    res = ResultadoSincronizacion(recibidas=len(datos.lecturas))
    for i, l in enumerate(datos.lecturas):
        disp = None
        if l.dispositivo_id is not None:
            disp = db.get(Dispositivo, l.dispositivo_id)
            if not disp or disp.usuario_id != u.id:
                res.rechazadas += 1
                res.errores.append(f"Lectura {i}: dispositivo no válido")
                continue
        entrada = LecturaEntrada.model_validate(l.model_dump(exclude={"fuente", "dispositivo_id"}))
        r = registrar_lectura(db, u, entrada, l.fuente, dispositivo=disp, commit=False)
        if r.duplicada:
            res.duplicadas += 1
        else:
            res.nuevas += 1
            if r.alerta:
                db.flush()
                res.alertas.append(AlertaSalida.model_validate(r.alerta))
    db.commit()
    return res


@router.get("/hbpm")
def protocolo_hbpm(dias: int = Query(7, ge=3, le=30), u: Usuario = Depends(usuario_actual),
                   db: Session = Depends(obtener_db)):
    """Promedio del monitoreo en casa (mañana y noche, 3 a 7 días)."""
    return resumen_hbpm(consultar_lecturas(db, u.id), hasta=ahora().date(), dias=dias)


@router.get("/tendencias")
def ver_tendencias(agrupacion: Literal["dia", "semana", "mes"] = "dia",
                   desde: datetime | None = None, hasta: datetime | None = None,
                   u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    return tendencias(consultar_lecturas(db, u.id, desde, hasta), agrupacion)


@router.delete("/{lectura_id}", status_code=204)
def eliminar(lectura_id: int, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    db.delete(obtener_propio(db, Lectura, lectura_id, u, "Lectura"))
    db.commit()
