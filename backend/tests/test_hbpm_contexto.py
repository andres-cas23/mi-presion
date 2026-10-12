from dataclasses import dataclass
from datetime import date, datetime

from app.models.enums import Contexto
from app.services.contexto import inferir_contexto
from app.services.hbpm import resumen_hbpm, tendencias


@dataclass
class L:
    sistolica: int
    diastolica: int
    medido_en: datetime
    pulso: int | None = 70


def semana(sis, dia, dias=7):
    out = []
    for d in range(1, dias + 1):
        for h, m in ((7, 0), (7, 2), (20, 0), (20, 2)):
            out.append(L(sis, dia, datetime(2026, 9, d, h, m)))
    return out


def test_protocolo_ideal_y_promedio():
    r = resumen_hbpm(semana(130, 82), hasta=date(2026, 9, 7))
    assert r.protocolo_minimo_cumplido and r.protocolo_ideal_cumplido
    assert r.dias_completos == 7 and r.total_lecturas == 28
    assert r.promedio_sistolica == 130 and r.supera_umbral_domiciliario is False


def test_umbral_domiciliario_135_85():
    r = resumen_hbpm(semana(136, 80), hasta=date(2026, 9, 7))
    assert r.supera_umbral_domiciliario is True


def test_protocolo_incompleto():
    r = resumen_hbpm(semana(130, 80, dias=2), hasta=date(2026, 9, 7))
    assert not r.protocolo_minimo_cumplido
    assert "Faltan 1" in r.interpretacion


def test_tendencias_semanales():
    t = tendencias(semana(130, 80), "semana")
    assert sum(g["n"] for g in t) == 28


def test_contexto_por_horario_de_medicacion():
    hs = ["08:00", "20:00"]
    assert inferir_contexto(datetime(2026, 9, 1, 7, 30), hs) == Contexto.ANTES_MEDICACION
    assert inferir_contexto(datetime(2026, 9, 1, 9, 0), hs) == Contexto.DESPUES_MEDICACION
    assert inferir_contexto(datetime(2026, 9, 1, 14, 0), hs) is None
    # cruce de medianoche: toma a las 23:30, lectura a las 00:30 del día siguiente
    assert inferir_contexto(datetime(2026, 9, 2, 0, 30), ["23:30"]) == Contexto.DESPUES_MEDICACION
