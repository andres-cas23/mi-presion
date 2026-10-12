"""Tablas `usuarios` y `perfiles_clinicos` (RF-01)."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.cifrado import TextoCifrado
from app.core.tiempo import ahora
from app.db.base import Base

if TYPE_CHECKING:
    from app.models import Alerta, Dispositivo, Lectura, Medicamento, Recordatorio


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    nombre: Mapped[str] = mapped_column(String(120))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)
    # Ley 1581 de 2012: constancia del consentimiento para tratar datos de salud
    consentimiento_fecha: Mapped[datetime] = mapped_column(DateTime)
    consentimiento_version: Mapped[str] = mapped_column(String(20))

    # Relaciones: "un usuario tiene muchas lecturas, medicamentos...".
    # cascade="all, delete-orphan" -> si se borra el usuario, se borra todo lo suyo.
    perfil: Mapped["PerfilClinico"] = relationship(back_populates="usuario", uselist=False,
                                                   cascade="all, delete-orphan")
    medicamentos: Mapped[list["Medicamento"]] = relationship(cascade="all, delete-orphan")
    dispositivos: Mapped[list["Dispositivo"]] = relationship(cascade="all, delete-orphan")
    lecturas: Mapped[list["Lectura"]] = relationship(cascade="all, delete-orphan")
    alertas: Mapped[list["Alerta"]] = relationship(cascade="all, delete-orphan")
    recordatorios: Mapped[list["Recordatorio"]] = relationship(cascade="all, delete-orphan")


class PerfilClinico(Base):
    __tablename__ = "perfiles_clinicos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True)
    sistolica_habitual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    diastolica_habitual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Meta ESC 2024: sistólica 120-129 mmHg en la mayoría de adultos si se tolera
    meta_sistolica_min: Mapped[int] = mapped_column(Integer, default=120)
    meta_sistolica_max: Mapped[int] = mapped_column(Integer, default=129)
    meta_diastolica_max: Mapped[int] = mapped_column(Integer, default=79)
    factores_riesgo: Mapped[str | None] = mapped_column(TextoCifrado, nullable=True)  # lista en JSON, cifrada
    antecedentes: Mapped[str | None] = mapped_column(TextoCifrado, nullable=True)
    medico_tratante: Mapped[str | None] = mapped_column(TextoCifrado, nullable=True)

    usuario: Mapped[Usuario] = relationship(back_populates="perfil")
