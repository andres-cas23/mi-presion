"""Mediciones de presión, alertas y resultados de sincronización."""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.tiempo import a_hora_local
from app.models.enums import Contexto, Fuente
from app.schemas.comun import DesdeModelo


class LecturaEntrada(BaseModel):
    sistolica: int = Field(ge=50, le=300)
    diastolica: int = Field(ge=30, le=200)
    pulso: int | None = Field(None, ge=25, le=250)
    medido_en: datetime | None = None
    contexto: Contexto | None = None
    notas: str | None = Field(None, max_length=500)
    id_externo: str | None = Field(None, max_length=120,
                                   description="Identificador en el origen; evita duplicados al sincronizar")

    @model_validator(mode="after")
    def _coherencia(self):
        if self.sistolica <= self.diastolica:
            raise ValueError("El número de arriba (sistólica) debe ser mayor que el de abajo (diastólica)")
        if self.medido_en is not None:
            self.medido_en = a_hora_local(self.medido_en)
        return self


class LecturaPlataforma(LecturaEntrada):
    """Lectura que llega desde Apple Health, Google Fit o Samsung Health."""
    fuente: Fuente
    dispositivo_id: int | None = None

    @field_validator("fuente")
    @classmethod
    def _no_manual(cls, v: Fuente) -> Fuente:
        if v == Fuente.MANUAL:
            raise ValueError("Use /lecturas/manual para el registro manual")
        return v


class SincronizacionLote(BaseModel):
    lecturas: list[LecturaPlataforma] = Field(min_length=1, max_length=1000)


class AlertaSalida(DesdeModelo):
    id: int
    lectura_id: int
    nivel: str
    mensaje: str
    creada_en: datetime
    atendida: bool


class LecturaSalida(DesdeModelo):
    id: int
    sistolica: int
    diastolica: int
    pulso: int | None
    presion_arterial_media: float | None
    medido_en: datetime
    fuente: str
    dispositivo_id: int | None
    contexto: str
    contexto_inferido: bool
    categoria: str
    en_meta: bool
    pulso_irregular: bool
    movimiento_detectado: bool
    notas: str | None


class ResultadoRegistro(BaseModel):
    lectura: LecturaSalida
    alerta: AlertaSalida | None = None
    mensaje: str
    duplicada: bool = False


class ResultadoSincronizacion(BaseModel):
    recibidas: int
    nuevas: int = 0
    duplicadas: int = 0
    rechazadas: int = 0
    errores: list[str] = []
    alertas: list[AlertaSalida] = []
