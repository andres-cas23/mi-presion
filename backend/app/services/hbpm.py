"""Protocolo de monitoreo domiciliario (HBPM) y tendencias (RF-04).

Protocolo (ESC 2024 / ACC-AHA 2017): dos mediciones por sesión, mañana y noche,
durante mínimo 3 días e idealmente 7 días consecutivos; se promedian las lecturas.

Nota clínica: para el PROMEDIO domiciliario el umbral de hipertensión de las
guías europeas es 135/85 mmHg (más bajo que el 140/90 de consultorio).
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from statistics import mean
from typing import Iterable, Literal, Protocol

UMBRAL_DOMICILIARIO = (135, 85)
DIAS_MINIMOS = 3
DIAS_IDEALES = 7


class LecturaLike(Protocol):
    sistolica: int
    diastolica: int
    pulso: int | None
    medido_en: datetime


def periodo_del_dia(dt: datetime) -> Literal["manana", "noche", "otro"]:
    if 4 <= dt.hour < 12:
        return "manana"
    if 17 <= dt.hour <= 23:
        return "noche"
    return "otro"


@dataclass
class ResumenHBPM:
    desde: date
    hasta: date
    total_lecturas: int
    dias_con_lecturas: int
    dias_completos: int  # días con al menos una lectura en la mañana y otra en la noche
    promedio_sistolica: float | None
    promedio_diastolica: float | None
    promedio_pulso: float | None
    protocolo_minimo_cumplido: bool
    protocolo_ideal_cumplido: bool
    supera_umbral_domiciliario: bool | None
    interpretacion: str
    detalle_por_dia: list[dict] = field(default_factory=list)


def _r(x: float | None) -> float | None:
    return None if x is None else round(x, 1)


def resumen_hbpm(lecturas: Iterable[LecturaLike], hasta: date, dias: int = DIAS_IDEALES) -> ResumenHBPM:
    desde = hasta - timedelta(days=dias - 1)
    en_ventana = [l for l in lecturas if desde <= l.medido_en.date() <= hasta]

    por_dia: dict[date, dict[str, list]] = defaultdict(lambda: {"manana": [], "noche": [], "otro": []})
    for l in en_ventana:
        por_dia[l.medido_en.date()][periodo_del_dia(l.medido_en)].append(l)

    dias_completos = sum(1 for d in por_dia.values() if d["manana"] and d["noche"])
    detalle = []
    for d in sorted(por_dia):
        todas = por_dia[d]["manana"] + por_dia[d]["noche"] + por_dia[d]["otro"]
        detalle.append({
            "fecha": d.isoformat(),
            "lecturas_manana": len(por_dia[d]["manana"]),
            "lecturas_noche": len(por_dia[d]["noche"]),
            "promedio_sistolica": _r(mean(l.sistolica for l in todas)),
            "promedio_diastolica": _r(mean(l.diastolica for l in todas)),
        })

    if en_ventana:
        ps = mean(l.sistolica for l in en_ventana)
        pd = mean(l.diastolica for l in en_ventana)
        pulsos = [l.pulso for l in en_ventana if l.pulso]
        pp = mean(pulsos) if pulsos else None
        supera = ps >= UMBRAL_DOMICILIARIO[0] or pd >= UMBRAL_DOMICILIARIO[1]
    else:
        ps = pd = pp = None
        supera = None

    minimo = len(por_dia) >= DIAS_MINIMOS
    ideal = dias_completos >= DIAS_IDEALES

    if not en_ventana:
        interp = "Aún no hay mediciones en este periodo."
    elif not minimo:
        faltan = DIAS_MINIMOS - len(por_dia)
        interp = (f"Faltan {faltan} día(s) de mediciones para un promedio confiable. "
                  "Mida en la mañana y en la noche, dos veces cada vez.")
    elif supera:
        interp = (f"Su promedio en casa ({ps:.0f}/{pd:.0f}) está por encima de 135/85. "
                  "Comparta este informe con su médico.")
    else:
        interp = f"Su promedio en casa ({ps:.0f}/{pd:.0f}) está por debajo de 135/85."

    return ResumenHBPM(desde, hasta, len(en_ventana), len(por_dia), dias_completos,
                       _r(ps), _r(pd), _r(pp), minimo, ideal, supera, interp, detalle)


def _clave(dt: datetime, agrupacion: str) -> str:
    if agrupacion == "dia":
        return dt.date().isoformat()
    if agrupacion == "semana":
        a, s, _ = dt.isocalendar()
        return f"{a}-S{s:02d}"
    return f"{dt.year}-{dt.month:02d}"


def tendencias(lecturas: Iterable[LecturaLike], agrupacion: Literal["dia", "semana", "mes"]) -> list[dict]:
    grupos: dict[str, list] = defaultdict(list)
    for l in lecturas:
        grupos[_clave(l.medido_en, agrupacion)].append(l)
    salida = []
    for k in sorted(grupos):
        g = grupos[k]
        pulsos = [l.pulso for l in g if l.pulso]
        salida.append({
            "periodo": k,
            "n": len(g),
            "promedio_sistolica": _r(mean(l.sistolica for l in g)),
            "promedio_diastolica": _r(mean(l.diastolica for l in g)),
            "promedio_pulso": _r(mean(pulsos)) if pulsos else None,
            "max_sistolica": max(l.sistolica for l in g),
            "min_sistolica": min(l.sistolica for l in g),
            "max_diastolica": max(l.diastolica for l in g),
            "min_diastolica": min(l.diastolica for l in g),
        })
    return salida
