"""Configuración de la aplicación.

Todos los valores secretos o que cambian entre computadores (claves, dirección
de la base de datos, llave de Gemini) se leen de VARIABLES DE ENTORNO:
  - En su computador: del archivo backend/.env (nunca se sube a GitHub).
  - En Render: de la sección "Environment" del servicio.
"""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- General ---
    nombre_app: str = "Mi Presión API"
    zona_horaria: str = "America/Bogota"
    version_consentimiento: str = "1.0"

    # --- Base de datos ---
    # Sin valor -> SQLite local (archivo mi_presion.db), ideal para practicar.
    # Con la URL de Supabase -> PostgreSQL en la nube.
    database_url: str = "sqlite:///./mi_presion.db"

    # --- Seguridad ---
    secret_key: str = "clave-de-desarrollo-cambiela"   # firma los tokens de sesión
    encryption_key: str = ""                          # cifra los datos clínicos (no cambiar después)
    access_token_expire_minutes: int = 60 * 8

    # --- Quién puede llamar a la API (CORS) ---
    # "*" = cualquier página. En producción ponga la URL de su frontend.
    cors_origins: str = "*"

    # --- Asistente con Gemini ---
    gemini_api_key: str = ""
    gemini_modelo: str = "gemini-3.5-flash-lite"
    asistente_limite_por_hora: int = 20

    @field_validator("database_url")
    @classmethod
    def _normalizar_url(cls, v: str) -> str:
        """Supabase entrega URLs 'postgresql://...'. SQLAlchemy necesita saber qué
        controlador usar, así que las convertimos a 'postgresql+psycopg://...'."""
        v = v.strip()
        if not v:                                   # si viene vacía...
            return "sqlite:///./mi_presion.db"      # ...usamos SQLite local
        for prefijo in ("postgres://", "postgresql://"):
            if v.startswith(prefijo):
                return "postgresql+psycopg://" + v[len(prefijo):]
        return v

    @property
    def es_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")

    @property
    def lista_cors(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def obtener_settings() -> Settings:
    return Settings()


settings = obtener_settings()
