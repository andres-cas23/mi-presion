"""Manejo de fecha y hora.

Las mediciones se guardan en la hora local del paciente (Colombia), porque el
protocolo de monitoreo habla de "mañana" y "noche" locales.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings

ZONA = ZoneInfo(settings.zona_horaria)


def ahora() -> datetime:
    return datetime.now(ZONA).replace(tzinfo=None, microsecond=0)


def a_hora_local(dt: datetime) -> datetime:
    """Convierte una fecha con zona horaria a hora local de Colombia."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(ZONA).replace(tzinfo=None)
