"""Tabla `dispositivos`: tensiómetros y relojes vinculados (RF-02)."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    fabricante: Mapped[str] = mapped_column(String(60))
    modelo: Mapped[str] = mapped_column(String(80))
    direccion_ble: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fecha_compra: Mapped[date | None] = mapped_column(Date, nullable=True)
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
