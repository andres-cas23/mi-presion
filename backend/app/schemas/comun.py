"""Piezas compartidas por todos los esquemas."""
import re

from pydantic import BaseModel, ConfigDict

HORA_REGEX = r"^([01]\d|2[0-3]):[0-5]\d$"


def validar_hora(h: str) -> str:
    if not re.match(HORA_REGEX, h):
        raise ValueError(f"Hora inválida: {h} (use el formato HH:MM, por ejemplo 08:00)")
    return h


class DesdeModelo(BaseModel):
    """Permite convertir directamente un modelo de base de datos en respuesta JSON."""
    model_config = ConfigDict(from_attributes=True)
