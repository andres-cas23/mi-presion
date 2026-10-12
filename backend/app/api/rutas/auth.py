"""/auth: crear cuenta e iniciar sesión (RF-01)."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.seguridad import crear_token, encriptar_password, verificar_password
from app.core.tiempo import ahora
from app.db.sesion import obtener_db
from app.models import PerfilClinico, Usuario
from app.schemas import RegistroUsuario, Token, UsuarioSalida
from app.services.recordatorios import recordatorios_hbpm_por_defecto

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioSalida, status_code=201)
def registrar(datos: RegistroUsuario, db: Session = Depends(obtener_db)):
    email = datos.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese correo")
    usuario = Usuario(email=email, hashed_password=encriptar_password(datos.password), nombre=datos.nombre,
                      fecha_nacimiento=datos.fecha_nacimiento, consentimiento_fecha=ahora(),
                      consentimiento_version=settings.version_consentimiento)
    usuario.perfil = PerfilClinico()
    db.add(usuario)
    db.flush()
    db.add_all(recordatorios_hbpm_por_defecto(usuario.id))
    db.commit()
    return usuario


@router.post("/token", response_model=Token)
def iniciar_sesion(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(obtener_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.email == form.username.lower().strip()))
    if not usuario or not verificar_password(form.password, usuario.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos")
    return Token(access_token=crear_token(usuario.id))
