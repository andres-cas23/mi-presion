"""Preguntas y respuestas del asistente con Gemini."""
from typing import Literal

from pydantic import BaseModel, Field


class MensajeChat(BaseModel):
    rol: Literal["usuario", "asistente"]
    texto: str = Field(min_length=1, max_length=4000)


class Pregunta(BaseModel):
    pregunta: str = Field(min_length=2, max_length=1000)
    historial: list[MensajeChat] = Field(default=[], max_length=20,
                                         description="Mensajes anteriores de esta conversación")
    usar_mis_datos: bool = Field(True, description="Permite usar el resumen de sus mediciones para responder")


class Respuesta(BaseModel):
    respuesta: str
    urgente: bool = False
    modelo: str


class EstadoAsistente(BaseModel):
    configurado: bool
    modelo: str
    limite_por_hora: int
