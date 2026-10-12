"""Recordatorios de medición, medicación y citas (RF-06).

El cálculo de próximos recordatorios vive en el backend; el envío push se
delega a un `Notificador` intercambiable. En producción se implementa con
Firebase Cloud Messaging (firebase-admin) según la arquitectura propuesta.
"""
import logging
from datetime import datetime, timedelta
from typing import Protocol

from app.models.enums import TipoRecordatorio
from app.models import Recordatorio

log = logging.getLogger(__name__)


def proximas_ocurrencias(recs: list[Recordatorio], desde: datetime, horas: int = 24):
    hasta = desde + timedelta(hours=horas)
    salida: list[tuple[Recordatorio, datetime]] = []
    for r in recs:
        if not r.activo:
            continue
        hh, mm = map(int, r.hora.split(":"))
        if r.tipo == TipoRecordatorio.CITA.value:
            if r.fecha:
                # Aviso de cita: se programa a la hora indicada del día de la cita
                momento = datetime.combine(r.fecha, datetime.min.time()).replace(hour=hh, minute=mm)
                if desde <= momento <= hasta:
                    salida.append((r, momento))
            continue
        dia = desde.date()
        while datetime.combine(dia, datetime.min.time()) <= hasta:
            momento = datetime.combine(dia, datetime.min.time()).replace(hour=hh, minute=mm)
            if str(momento.weekday()) in r.dias_semana and desde <= momento <= hasta:
                salida.append((r, momento))
            dia += timedelta(days=1)
    return sorted(salida, key=lambda x: x[1])


def recordatorios_hbpm_por_defecto(usuario_id: int) -> list[Recordatorio]:
    """Plan HBPM: medir mañana y noche (dos lecturas separadas 1-2 minutos)."""
    return [
        Recordatorio(usuario_id=usuario_id, tipo=TipoRecordatorio.MEDICION.value, hora="07:00",
                     titulo="Mida su presión: 2 tomas, con 1-2 minutos entre cada una (antes del medicamento)"),
        Recordatorio(usuario_id=usuario_id, tipo=TipoRecordatorio.MEDICION.value, hora="19:00",
                     titulo="Mida su presión: 2 tomas, con 1-2 minutos entre cada una"),
    ]


class Notificador(Protocol):
    def enviar(self, usuario_id: int, titulo: str, cuerpo: str) -> None: ...


class NotificadorLog:
    """Implementación de desarrollo: solo registra en el log."""

    def enviar(self, usuario_id: int, titulo: str, cuerpo: str) -> None:
        log.info("[PUSH] usuario=%s | %s | %s", usuario_id, titulo, cuerpo)


# Ejemplo de implementación con FCM (requiere `pip install firebase-admin`):
#
# class NotificadorFCM:
#     def __init__(self, obtener_token_dispositivo):
#         import firebase_admin
#         firebase_admin.initialize_app()
#         self._token = obtener_token_dispositivo
#
#     def enviar(self, usuario_id, titulo, cuerpo):
#         from firebase_admin import messaging
#         messaging.send(messaging.Message(
#             token=self._token(usuario_id),
#             notification=messaging.Notification(title=titulo, body=cuerpo)))
