"""Tabla `recordatorios`: medición, medicamento o cita (RF-06)."""
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Recordatorio(Base):
    __tablename__ = "recordatorios"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    titulo: Mapped[str] = mapped_column(String(160))
    hora: Mapped[str] = mapped_column(String(5))                            # "HH:MM"
    dias_semana: Mapped[str] = mapped_column(String(7), default="0123456")  # 0 = lunes
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)         # solo para citas
    medicamento_id: Mapped[int | None] = mapped_column(
        ForeignKey("medicamentos.id", ondelete="CASCADE"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
