"""Ley 1581 de 2012: derechos del titular (conocer, exportar y suprimir sus datos)."""
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.sesion import obtener_db
from app.api.dependencias import usuario_actual
from app.models import Usuario
from app.schemas import (AlertaSalida, DispositivoSalida, LecturaSalida, MedicamentoSalida,
                         RecordatorioSalida, UsuarioSalida)
from app.core.tiempo import ahora

router = APIRouter(prefix="/privacidad", tags=["Privacidad"])

POLITICA = {
    "version": settings.version_consentimiento,
    "resumen": [
        "Sus datos de salud son datos sensibles y solo se usan para ayudarle a controlar su presión.",
        "No vendemos ni compartimos sus datos. Solo usted decide si enviar un informe a su médico.",
        "Sus datos viajan cifrados y se guardan cifrados.",
        "Puede descargar toda su información o borrar su cuenta cuando quiera desde la aplicación.",
        "Si los datos se usan para investigación, será solo con su permiso y sin datos que lo identifiquen.",
    ],
    "marco_legal": "Ley 1581 de 2012 y Decreto 1377 de 2013 (República de Colombia)",
}


@router.get("/politica")
def politica():
    return POLITICA


@router.get("/exportar")
def exportar_mis_datos(u: Usuario = Depends(usuario_actual)):
    p = u.perfil
    return {
        "exportado_en": ahora().isoformat(),
        "usuario": UsuarioSalida.model_validate(u).model_dump(mode="json"),
        "perfil_clinico": {
            "sistolica_habitual": p.sistolica_habitual, "diastolica_habitual": p.diastolica_habitual,
            "meta_sistolica": [p.meta_sistolica_min, p.meta_sistolica_max],
            "meta_diastolica_max": p.meta_diastolica_max,
            "factores_riesgo": json.loads(p.factores_riesgo) if p.factores_riesgo else [],
            "antecedentes": p.antecedentes, "medico_tratante": p.medico_tratante,
        } if p else None,
        "medicamentos": [MedicamentoSalida.model_validate(m).model_dump(mode="json") for m in u.medicamentos],
        "dispositivos": [DispositivoSalida.model_validate(d).model_dump(mode="json") for d in u.dispositivos],
        "lecturas": [LecturaSalida.model_validate(l).model_dump(mode="json") for l in u.lecturas],
        "alertas": [AlertaSalida.model_validate(a).model_dump(mode="json") for a in u.alertas],
        "recordatorios": [RecordatorioSalida.model_validate(r).model_dump(mode="json") for r in u.recordatorios],
    }


@router.delete("/cuenta", status_code=204)
def eliminar_cuenta(u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    """Supresión total e irreversible de la cuenta y todos sus datos."""
    db.delete(u)
    db.commit()
