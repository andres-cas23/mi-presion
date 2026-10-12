"""Clasificación de lecturas según guías ESC 2024 y generación de alertas (RF-05).

Categorías ESC 2024 (lectura individual):
  - No elevada:   PAS < 120  y PAD < 70
  - Elevada:      PAS 120-139 o PAD 70-89
  - Hipertensión: PAS >= 140 o PAD >= 90
  - Crisis (alerta urgente del producto): PAS >= 180 o PAD >= 120

Se toma la categoría más alta que alcance cualquiera de los dos valores.
"""
from dataclasses import dataclass

from app.models.enums import Categoria, NivelAlerta

UMBRAL_CRISIS = (180, 120)
UMBRAL_HIPERTENSION = (140, 90)
UMBRAL_ELEVADA = (120, 70)
UMBRAL_HIPOTENSION = (90, 60)


@dataclass(frozen=True)
class Resultado:
    categoria: Categoria
    nivel_alerta: NivelAlerta | None
    mensaje: str


MENSAJES = {
    Categoria.NO_ELEVADA: "Su presión está en un rango no elevado. ¡Siga así!",
    Categoria.ELEVADA: ("Su presión está elevada. Mantenga sus hábitos saludables "
                        "y siga midiendo según su plan."),
    Categoria.HIPERTENSION: ("Su presión está en rango de hipertensión. Si se repite, "
                             "compártalo con su médico."),
    Categoria.CRISIS: ("Su presión está muy alta (180/120 o más). Siéntese, descanse 5 minutos "
                       "y vuelva a medir. Si sigue igual o tiene dolor en el pecho, falta de aire, "
                       "dolor de cabeza fuerte, visión borrosa, confusión o debilidad en un lado "
                       "del cuerpo, llame a la línea de emergencias 123 o acuda a urgencias."),
}

MENSAJE_HIPOTENSION = ("Su presión está baja (menos de 90/60). Si se siente mareado o débil, "
                       "siéntese o acuéstese y consulte a su médico.")


def clasificar(sistolica: int, diastolica: int) -> Resultado:
    if sistolica >= UMBRAL_CRISIS[0] or diastolica >= UMBRAL_CRISIS[1]:
        return Resultado(Categoria.CRISIS, NivelAlerta.URGENTE, MENSAJES[Categoria.CRISIS])
    if sistolica >= UMBRAL_HIPERTENSION[0] or diastolica >= UMBRAL_HIPERTENSION[1]:
        cat = Categoria.HIPERTENSION
    elif sistolica >= UMBRAL_ELEVADA[0] or diastolica >= UMBRAL_ELEVADA[1]:
        cat = Categoria.ELEVADA
    else:
        cat = Categoria.NO_ELEVADA

    if sistolica < UMBRAL_HIPOTENSION[0] or diastolica < UMBRAL_HIPOTENSION[1]:
        return Resultado(cat, NivelAlerta.ADVERTENCIA, MENSAJE_HIPOTENSION)
    return Resultado(cat, None, MENSAJES[cat])


def en_meta(sistolica: int, diastolica: int, meta_sis_max: int = 129, meta_dia_max: int = 79) -> bool:
    """Meta terapéutica personalizada (por defecto ESC 2024: PAS 120-129).

    Se evalúa solo el límite superior: una lectura por debajo del mínimo no se
    considera 'fuera de meta' por sí misma; la hipotensión se maneja con su alerta.
    """
    return sistolica <= meta_sis_max and diastolica <= meta_dia_max
