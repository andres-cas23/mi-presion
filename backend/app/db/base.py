"""Clase madre de todas las tablas. Cada modelo en app/models hereda de Base."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
