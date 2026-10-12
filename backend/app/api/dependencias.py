"""Piezas que las rutas piden "prestadas" (inyección de dependencias).

`usuario_actual` lee el token que envía el navegador y devuelve el usuario.
Cualquier ruta que lo pida queda automáticamente protegida: sin sesión, no entra.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.seguridad import leer_token
from app.db.sesion import obtener_db
from app.models import Usuario

esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")


def usuario_actual(token: str = Depends(esquema_oauth2), db: Session = Depends(obtener_db)) -> Usuario:
    usuario_id = leer_token(token)
    usuario = db.get(Usuario, usuario_id) if usuario_id else None
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Su sesión terminó. Ingrese de nuevo.",
                            headers={"WWW-Authenticate": "Bearer"})
    return usuario


def obtener_propio(db: Session, modelo, objeto_id: int, usuario: Usuario, nombre: str):
    """Busca un registro y verifica que pertenezca al usuario (nadie ve datos ajenos)."""
    objeto = db.get(modelo, objeto_id)
    if not objeto or objeto.usuario_id != usuario.id:
        raise HTTPException(404, f"{nombre} no encontrado")
    return objeto
