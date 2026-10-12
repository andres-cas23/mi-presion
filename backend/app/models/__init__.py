"""MODELOS = las tablas de la base de datos (equivale a models.py en Django).

Cada clase es una tabla en Supabase y cada atributo es una columna.
Se importan todas aquí para poder escribir, en cualquier parte del código:
    from app.models import Usuario, Lectura
"""
from app.models.dispositivo import Dispositivo
from app.models.lectura import Alerta, Lectura
from app.models.medicamento import Medicamento
from app.models.recordatorio import Recordatorio
from app.models.usuario import PerfilClinico, Usuario

__all__ = ["Usuario", "PerfilClinico", "Medicamento", "Dispositivo", "Lectura", "Alerta", "Recordatorio"]
