"""Registro, inicio de sesión y datos públicos del usuario."""
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.comun import DesdeModelo


class RegistroUsuario(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nombre: str = Field(min_length=2, max_length=120)
    fecha_nacimiento: date | None = None
    acepta_tratamiento_datos: bool = Field(
        description="Consentimiento explícito para tratar datos de salud (Ley 1581 de 2012)")

    @field_validator("acepta_tratamiento_datos")
    @classmethod
    def _consentimiento(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debe aceptar el tratamiento de datos para crear la cuenta")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioSalida(DesdeModelo):
    id: int
    email: EmailStr
    nombre: str
    fecha_nacimiento: date | None
    creado_en: datetime
    consentimiento_version: str
