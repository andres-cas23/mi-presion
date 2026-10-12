"""Tablas `lecturas` (cada medición de presión) y `alertas`."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.cifrado import TextoCifrado
from app.core.tiempo import ahora
from app.db.base import Base


class Lectura(Base):
    """Todas las fuentes (Bluetooth, plataformas de salud, manual) terminan aquí."""
    __tablename__ = "lecturas"
    # Evita guardar dos veces la misma medición al sincronizar de nuevo
    __table_args__ = (UniqueConstraint("usuario_id", "id_externo", name="uq_lectura_externa"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    dispositivo_id: Mapped[int | None] = mapped_column(
        ForeignKey("dispositivos.id", ondelete="SET NULL"), nullable=True)
    sistolica: Mapped[int] = mapped_column(Integer)
    diastolica: Mapped[int] = mapped_column(Integer)
    pulso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_arterial_media: Mapped[float | None] = mapped_column(Float, nullable=True)
    medido_en: Mapped[datetime] = mapped_column(DateTime, index=True)
    fuente: Mapped[str] = mapped_column(String(30))
    contexto: Mapped[str] = mapped_column(String(30))
    contexto_inferido: Mapped[bool] = mapped_column(Boolean, default=False)
    categoria: Mapped[str] = mapped_column(String(30))
    en_meta: Mapped[bool] = mapped_column(Boolean)
    pulso_irregular: Mapped[bool] = mapped_column(Boolean, default=False)
    movimiento_detectado: Mapped[bool] = mapped_column(Boolean, default=False)
    id_externo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notas: Mapped[str | None] = mapped_column(TextoCifrado, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    lectura_id: Mapped[int] = mapped_column(ForeignKey("lecturas.id", ondelete="CASCADE"))
    nivel: Mapped[str] = mapped_column(String(20))
    mensaje: Mapped[str] = mapped_column(String(600))
    creada_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)
    atendida: Mapped[bool] = mapped_column(Boolean, default=False)

    lectura: Mapped[Lectura] = relationship()
