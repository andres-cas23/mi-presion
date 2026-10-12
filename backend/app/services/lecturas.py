"""Ruta única de registro de lecturas.

Tal como plantea la arquitectura del documento, la lectura manual, la de
Bluetooth y la de plataformas de salud convergen aquí desde el paso de
etiquetado: contexto -> clasificación -> alerta -> almacenamiento.
"""
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import Contexto, Fuente
from app.models import Alerta, Dispositivo, Lectura, Medicamento, Usuario
from app.schemas import LecturaEntrada
from app.services.clasificacion import clasificar, en_meta
from app.services.contexto import inferir_contexto
from app.core.tiempo import ahora


@dataclass
class Registro:
    lectura: Lectura
    alerta: Alerta | None
    mensaje: str
    duplicada: bool = False


def _horarios_medicacion(db: Session, usuario_id: int) -> list[str]:
    meds = db.scalars(select(Medicamento).where(Medicamento.usuario_id == usuario_id,
                                                Medicamento.activo.is_(True)))
    return [h for m in meds for h in m.horarios.split(",") if h]


def registrar_lectura(db: Session, usuario: Usuario, datos: LecturaEntrada, fuente: Fuente,
                      dispositivo: Dispositivo | None = None, pam: float | None = None,
                      pulso_irregular: bool = False, movimiento: bool = False,
                      commit: bool = True) -> Registro:
    # 1. Deduplicación (sincronizaciones repetidas o reintentos offline)
    if datos.id_externo:
        existente = db.scalar(select(Lectura).where(Lectura.usuario_id == usuario.id,
                                                    Lectura.id_externo == datos.id_externo))
        if existente:
            return Registro(existente, None, "Lectura ya registrada anteriormente", duplicada=True)

    # 2. Etiquetado: fecha/hora y contexto
    medido_en = datos.medido_en or ahora()
    contexto, inferido = datos.contexto, False
    if contexto is None:
        contexto = inferir_contexto(medido_en, _horarios_medicacion(db, usuario.id))
        inferido = contexto is not None
        contexto = contexto or Contexto.SIN_ESPECIFICAR

    # 3. Clasificación clínica y meta personal
    res = clasificar(datos.sistolica, datos.diastolica)
    perfil = usuario.perfil
    meta_ok = en_meta(datos.sistolica, datos.diastolica,
                      perfil.meta_sistolica_max if perfil else 129,
                      perfil.meta_diastolica_max if perfil else 79)

    lectura = Lectura(
        usuario_id=usuario.id, dispositivo_id=dispositivo.id if dispositivo else None,
        sistolica=datos.sistolica, diastolica=datos.diastolica, pulso=datos.pulso,
        presion_arterial_media=pam, medido_en=medido_en, fuente=fuente.value,
        contexto=contexto.value, contexto_inferido=inferido, categoria=res.categoria.value,
        en_meta=meta_ok, pulso_irregular=pulso_irregular, movimiento_detectado=movimiento,
        id_externo=datos.id_externo, notas=datos.notas,
    )
    db.add(lectura)
    db.flush()

    # 4. Alertas
    alerta = None
    mensaje = res.mensaje
    if pulso_irregular:
        mensaje += " El tensiómetro detectó pulso irregular; coménteselo a su médico."
    if res.nivel_alerta:
        alerta = Alerta(usuario_id=usuario.id, lectura_id=lectura.id,
                        nivel=res.nivel_alerta.value, mensaje=res.mensaje)
        db.add(alerta)

    if dispositivo:
        dispositivo.ultima_sincronizacion = ahora()

    if commit:
        db.commit()
    return Registro(lectura, alerta, mensaje)


def consultar_lecturas(db: Session, usuario_id: int, desde=None, hasta=None) -> list[Lectura]:
    """Lecturas del usuario ordenadas por fecha, opcionalmente filtradas por periodo."""
    q = select(Lectura).where(Lectura.usuario_id == usuario_id)
    if desde:
        q = q.where(Lectura.medido_en >= desde)
    if hasta:
        q = q.where(Lectura.medido_en <= hasta)
    return list(db.scalars(q.order_by(Lectura.medido_en)))
