"""Contraseñas y sesiones.

- Las contraseñas NUNCA se guardan tal cual: se guarda un "hash" (bcrypt), una
  huella que no se puede revertir.
- Al iniciar sesión se entrega un TOKEN (JWT): una especie de pase firmado que
  el navegador muestra en cada petición para demostrar quién es.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITMO = "HS256"


def encriptar_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verificar_password(password: str, hash_guardado: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hash_guardado.encode("utf-8"))


def crear_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, settings.secret_key, algorithm=ALGORITMO)


def leer_token(token: str) -> int | None:
    """Devuelve el id del usuario si el token es válido y no ha vencido."""
    try:
        sub = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO]).get("sub")
        return int(sub) if sub and sub.isdigit() else None
    except jwt.PyJWTError:
        return None
