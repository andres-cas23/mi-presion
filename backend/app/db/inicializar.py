"""Crea las tablas la primera vez que arranca la aplicación.

En Supabase además activa "Row Level Security" (RLS) en cada tabla. Supabase
publica automáticamente una API para las tablas del esquema `public`; con RLS
activado y sin políticas, esa API pública queda bloqueada y SOLO nuestro backend
(que se conecta como dueño de las tablas) puede leer y escribir los datos.
"""
import logging

from sqlalchemy import text

from app import models  # noqa: F401  (registra todos los modelos antes de crear tablas)
from app.core.config import settings
from app.db.base import Base
from app.db.sesion import engine

log = logging.getLogger(__name__)


def crear_tablas() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.es_postgres:
        with engine.begin() as con:
            for tabla in Base.metadata.sorted_tables:
                con.execute(text(f'ALTER TABLE "{tabla.name}" ENABLE ROW LEVEL SECURITY'))
        log.info("Tablas listas en PostgreSQL con RLS activado.")
