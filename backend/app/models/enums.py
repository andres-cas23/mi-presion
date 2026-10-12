"""Listas de valores permitidos (categorías, fuentes, contextos...)."""
from enum import Enum


class Categoria(str, Enum):
    """Clasificación ESC 2024 (presión en consultorio / lectura individual)."""
    NO_ELEVADA = "no_elevada"          # < 120/70
    ELEVADA = "elevada"                # 120-139 / 70-89
    HIPERTENSION = "hipertension"      # >= 140/90
    CRISIS = "crisis_hipertensiva"     # >= 180/120 (genera alerta urgente)


class Fuente(str, Enum):
    BLUETOOTH = "bluetooth"
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    SAMSUNG_HEALTH = "samsung_health"
    MANUAL = "manual"


class Contexto(str, Enum):
    ANTES_MEDICACION = "antes_medicacion"
    DESPUES_MEDICACION = "despues_medicacion"
    ANTES_ACTIVIDAD = "antes_actividad"
    DESPUES_ACTIVIDAD = "despues_actividad"
    REPOSO = "reposo"
    SIN_ESPECIFICAR = "sin_especificar"


class NivelAlerta(str, Enum):
    ADVERTENCIA = "advertencia"
    URGENTE = "urgente"


class TipoRecordatorio(str, Enum):
    MEDICION = "medicion"
    MEDICAMENTO = "medicamento"
    CITA = "cita"


class TipoDispositivo(str, Enum):
    TENSIOMETRO_BLE = "tensiometro_ble"
    RELOJ_O_BANDA = "reloj_o_banda"
