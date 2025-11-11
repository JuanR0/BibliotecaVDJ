"""
Módulo de configuración de la aplicación Biblioteca.

Este módulo contiene la configuración de la base de datos y
las dependencias de conexión para SQLAlchemy y FastAPI.
"""

from .database import (
    Base,
    engine,
    SessionLocal,
    get_db,
    create_tables
)

__all__ = [
    "Base",
    "engine", 
    "SessionLocal",
    "get_db",
    "create_tables"
]

