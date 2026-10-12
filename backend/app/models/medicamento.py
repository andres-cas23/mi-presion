"""Tabla `medicamentos`. Nombre y dosis se guardan cifrados."""
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.cifrado import TextoCifrado
from app.db.base import Base


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(TextoCifrado)
    dosis: Mapped[str | None] = mapped_column(TextoCifrado, nullable=True)
    horarios: Mapped[str] = mapped_column(String(200), default="")  # ejemplo: "08:00,20:00"
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
