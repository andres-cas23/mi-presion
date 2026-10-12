"""Inferencia automática del contexto de una lectura (RF-03).

Si la app no envía contexto, se deduce a partir de los horarios de medicación
del paciente: una lectura hasta 60 min antes de una toma se marca
'antes_medicacion' y hasta 180 min después, 'despues_medicacion'.
"""
from datetime import datetime, time, timedelta

from app.models.enums import Contexto

VENTANA_ANTES = timedelta(minutes=60)
VENTANA_DESPUES = timedelta(minutes=180)


def _a_time(h: str) -> time:
    hh, mm = h.split(":")
    return time(int(hh), int(mm))


def inferir_contexto(medido_en: datetime, horarios_medicacion: list[str]) -> Contexto | None:
    mejor: tuple[timedelta, Contexto] | None = None
    for h in horarios_medicacion:
        t = _a_time(h)
        # Revisa la toma del mismo día y de los días vecinos (cruces de medianoche)
        for desfase in (-1, 0, 1):
            toma = datetime.combine(medido_en.date() + timedelta(days=desfase), t)
            delta = medido_en - toma
            if -VENTANA_ANTES <= delta < timedelta(0):
                candidato = (abs(delta), Contexto.ANTES_MEDICACION)
            elif timedelta(0) <= delta <= VENTANA_DESPUES:
                candidato = (abs(delta), Contexto.DESPUES_MEDICACION)
            else:
                continue
            if mejor is None or candidato[0] < mejor[0]:
                mejor = candidato
    return mejor[1] if mejor else None
