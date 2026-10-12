"""/reportes: informes PDF, CSV y FHIR para el médico (RF-07)."""
from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.dependencias import usuario_actual
from app.core.tiempo import ahora
from app.db.sesion import obtener_db
from app.models import Usuario
from app.services.hbpm import resumen_hbpm
from app.services.lecturas import consultar_lecturas
from app.services.reportes import generar_bundle_fhir, generar_csv, generar_pdf

router = APIRouter(prefix="/reportes", tags=["Informes"])


def _adjunto(ext: str) -> dict:
    return {"Content-Disposition": f'attachment; filename="presion_arterial_{ahora():%Y%m%d}.{ext}"'}


@router.get("/csv")
def exportar_csv(desde: datetime | None = None, hasta: datetime | None = None,
                 u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    return Response(generar_csv(consultar_lecturas(db, u.id, desde, hasta)),
                    media_type="text/csv; charset=utf-8", headers=_adjunto("csv"))


@router.get("/pdf")
def exportar_pdf(desde: datetime | None = None, hasta: datetime | None = None,
                 u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    resumen = resumen_hbpm(consultar_lecturas(db, u.id), hasta=ahora().date())
    pdf = generar_pdf(u, consultar_lecturas(db, u.id, desde, hasta), resumen, desde, hasta)
    return Response(pdf, media_type="application/pdf", headers=_adjunto("pdf"))


@router.get("/fhir")
def exportar_fhir(desde: datetime | None = None, hasta: datetime | None = None,
                  u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    return generar_bundle_fhir(u, consultar_lecturas(db, u.id, desde, hasta))
