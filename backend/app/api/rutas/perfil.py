"""/perfil: datos clínicos y medicamentos (RF-01)."""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_propio, usuario_actual
from app.db.sesion import obtener_db
from app.models import Medicamento, PerfilClinico, Recordatorio, Usuario
from app.models.enums import TipoRecordatorio
from app.schemas import (MedicamentoEntrada, MedicamentoSalida, PerfilClinicoEntrada, PerfilClinicoSalida,
                         UsuarioSalida)

router = APIRouter(prefix="/perfil", tags=["Perfil"])


def _salida(u: Usuario) -> PerfilClinicoSalida:
    p = u.perfil
    return PerfilClinicoSalida(
        usuario=UsuarioSalida.model_validate(u),
        sistolica_habitual=p.sistolica_habitual, diastolica_habitual=p.diastolica_habitual,
        meta_sistolica_min=p.meta_sistolica_min, meta_sistolica_max=p.meta_sistolica_max,
        meta_diastolica_max=p.meta_diastolica_max,
        factores_riesgo=json.loads(p.factores_riesgo) if p.factores_riesgo else [],
        antecedentes=p.antecedentes, medico_tratante=p.medico_tratante)


@router.get("", response_model=PerfilClinicoSalida)
def ver_perfil(u: Usuario = Depends(usuario_actual)):
    return _salida(u)


@router.put("", response_model=PerfilClinicoSalida)
def actualizar_perfil(datos: PerfilClinicoEntrada, u: Usuario = Depends(usuario_actual),
                      db: Session = Depends(obtener_db)):
    if datos.meta_sistolica_min > datos.meta_sistolica_max:
        raise HTTPException(422, "La meta mínima no puede ser mayor que la máxima")
    p = u.perfil or PerfilClinico(usuario_id=u.id)
    for campo in ("sistolica_habitual", "diastolica_habitual", "meta_sistolica_min",
                  "meta_sistolica_max", "meta_diastolica_max", "antecedentes", "medico_tratante"):
        setattr(p, campo, getattr(datos, campo))
    p.factores_riesgo = json.dumps(datos.factores_riesgo, ensure_ascii=False)
    db.add(p)
    db.commit()
    db.refresh(u)
    return _salida(u)


@router.get("/medicamentos", response_model=list[MedicamentoSalida])
def listar_medicamentos(u: Usuario = Depends(usuario_actual)):
    return [m for m in u.medicamentos if m.activo]


@router.post("/medicamentos", response_model=MedicamentoSalida, status_code=201)
def agregar_medicamento(datos: MedicamentoEntrada, u: Usuario = Depends(usuario_actual),
                        db: Session = Depends(obtener_db)):
    m = Medicamento(usuario_id=u.id, nombre=datos.nombre, dosis=datos.dosis, horarios=",".join(datos.horarios))
    db.add(m)
    db.flush()
    if datos.crear_recordatorios:
        for h in datos.horarios:
            db.add(Recordatorio(usuario_id=u.id, tipo=TipoRecordatorio.MEDICAMENTO.value, hora=h,
                                titulo=f"Tome su medicamento: {datos.nombre}"
                                       + (f" ({datos.dosis})" if datos.dosis else ""),
                                medicamento_id=m.id))
    db.commit()
    return m


@router.delete("/medicamentos/{med_id}", status_code=204)
def suspender_medicamento(med_id: int, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    m = obtener_propio(db, Medicamento, med_id, u, "Medicamento")
    m.activo = False
    for r in u.recordatorios:
        if r.medicamento_id == m.id:
            r.activo = False
    db.commit()
