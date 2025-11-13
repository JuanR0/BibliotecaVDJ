"""
Módulo de configuración de la aplicación Biblioteca.

Este módulo contiene la configuración de la base de datos y
las dependencias de conexión para SQLAlchemy y FastAPI.
"""

from .database import (
    Base,
    engine,
    AsyncSessionLocal,  # ✅ CAMBIAR: SessionLocal → AsyncSessionLocal
    get_db,
    verify_connection,
    create_tables
)

__all__ = [
    "Base",
    "engine", 
    "AsyncSessionLocal",  # ✅ CAMBIAR
    "get_db",
    "verify_connection",
    "create_tables"
]
