"""Cifrado AES-256-GCM de los datos clínicos sensibles (Ley 1581 de 2012).

Aunque alguien lograra ver la base de datos en Supabase, campos como
antecedentes, medicamentos o notas aparecerían como texto ilegible.

IMPORTANTE: si cambia ENCRYPTION_KEY después de guardar datos, esos datos ya no
se podrán leer. Defínala una vez y no la vuelva a tocar.
"""
import base64
import binascii
import hashlib
import logging
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.core.config import settings

log = logging.getLogger(__name__)


def _clave() -> bytes:
    texto = settings.encryption_key.strip()
    if not texto:
        log.warning("ENCRYPTION_KEY no definida: se deriva de SECRET_KEY (solo para desarrollo).")
        return hashlib.sha256(settings.secret_key.encode()).digest()
    try:
        clave = base64.b64decode(texto, validate=True)
        if len(clave) == 32:
            return clave
    except (binascii.Error, ValueError):
        pass
    # Cualquier otro texto (p. ej. el generado por Render) se convierte en 32 bytes.
    return hashlib.sha256(texto.encode()).digest()


_aes = AESGCM(_clave())


def cifrar(texto: str) -> str:
    nonce = os.urandom(12)
    return base64.b64encode(nonce + _aes.encrypt(nonce, texto.encode("utf-8"), None)).decode()


def descifrar(token: str) -> str:
    datos = base64.b64decode(token)
    return _aes.decrypt(datos[:12], datos[12:], None).decode("utf-8")


class TextoCifrado(TypeDecorator):
    """Tipo de columna: se cifra al guardar y se descifra al leer, sin que el
    resto del código tenga que preocuparse."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else cifrar(value)

    def process_result_value(self, value, dialect):
        return None if value is None else descifrar(value)
