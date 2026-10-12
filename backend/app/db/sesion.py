"""Conexión a la base de datos.

- `engine` es la conexión permanente con Supabase (o SQLite).
- `obtener_db()` abre una "sesión" por cada petición y la cierra al terminar,
  como abrir y cerrar un cuaderno cada vez que se escribe algo.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

if settings.es_postgres:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,       # revisa que la conexión siga viva (Render duerme el servicio)
        pool_size=5, max_overflow=5,
        pool_recycle=300,
        # Desactiva "prepared statements": necesario si se usa el pooler en modo transacción
        connect_args={"prepare_threshold": None},
    )
else:
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _activar_llaves_foraneas(conexion, _):
        conexion.execute("PRAGMA foreign_keys=ON")


SesionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def obtener_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()
