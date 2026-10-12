"""Perfil clínico y medicamentos."""
from pydantic import BaseModel, Field, field_validator

from app.schemas.comun import DesdeModelo, validar_hora
from app.schemas.usuario import UsuarioSalida


class PerfilClinicoEntrada(BaseModel):
    sistolica_habitual: int | None = Field(None, ge=60, le=260)
    diastolica_habitual: int | None = Field(None, ge=30, le=160)
    meta_sistolica_min: int = Field(120, ge=90, le=160)
    meta_sistolica_max: int = Field(129, ge=100, le=170)
    meta_diastolica_max: int = Field(79, ge=60, le=100)
    factores_riesgo: list[str] = []
    antecedentes: str | None = None
    medico_tratante: str | None = None


class PerfilClinicoSalida(PerfilClinicoEntrada):
    usuario: UsuarioSalida


class MedicamentoEntrada(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    dosis: str | None = None
    horarios: list[str] = Field(default=[], description="Horas de toma en formato HH:MM")
    crear_recordatorios: bool = True

    @field_validator("horarios")
    @classmethod
    def _horas(cls, v: list[str]) -> list[str]:
        return sorted({validar_hora(h) for h in v})


class MedicamentoSalida(DesdeModelo):
    id: int
    nombre: str
    dosis: str | None
    horarios: list[str]
    activo: bool

    @field_validator("horarios", mode="before")
    @classmethod
    def _separar(cls, v):
        return [h for h in v.split(",") if h] if isinstance(v, str) else v
