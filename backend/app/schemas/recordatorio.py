"""Recordatorios."""
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import TipoRecordatorio
from app.schemas.comun import HORA_REGEX, DesdeModelo


class RecordatorioEntrada(BaseModel):
    tipo: TipoRecordatorio
    titulo: str = Field(min_length=1, max_length=160)
    hora: str = Field(pattern=HORA_REGEX)
    dias_semana: str = Field("0123456", pattern=r"^[0-6]{1,7}$", description="0 = lunes ... 6 = domingo")
    fecha: date | None = Field(None, description="Obligatoria para citas médicas")

    @model_validator(mode="after")
    def _cita(self):
        if self.tipo == TipoRecordatorio.CITA and self.fecha is None:
            raise ValueError("Las citas médicas requieren fecha")
        return self


class RecordatorioSalida(DesdeModelo):
    id: int
    tipo: str
    titulo: str
    hora: str
    dias_semana: str
    fecha: date | None
    medicamento_id: int | None
    activo: bool


class RecordatorioProximo(BaseModel):
    recordatorio: RecordatorioSalida
    programado_para: datetime
