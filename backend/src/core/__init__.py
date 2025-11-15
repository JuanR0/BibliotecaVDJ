# src/core/__init__.py
from .security import (
    obtener_hash_clave,
    verificar_clave,
    crear_token_acceso,
    verificar_token,
    obtener_usuario_actual,
    obtener_usuario_actual_optcional,
    autenticar_usuario,
    # ✅ NUEVAS funciones del sistema simplificado
    puede_consultar,
    puede_prestar,
    puede_gestionar_recursos,
    puede_gestionar_usuarios,
    requerir_usuario_activo,
    requerir_puede_consultar,
    requerir_puede_prestar,
    requerir_puede_gestionar_recursos,
    requerir_puede_gestionar_usuarios,
    obtener_permisos_frontend,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

__all__ = [
    "obtener_hash_clave",
    "verificar_clave",
    "crear_token_acceso", 
    "verificar_token",
    "obtener_usuario_actual",
    "obtener_usuario_actual_optcional",
    "autenticar_usuario",
    # ✅ NUEVAS funciones
    "puede_consultar",
    "puede_prestar", 
    "puede_gestionar_recursos",
    "puede_gestionar_usuarios",
    "requerir_usuario_activo",
    "requerir_puede_consultar",
    "requerir_puede_prestar",
    "requerir_puede_gestionar_recursos", 
    "requerir_puede_gestionar_usuarios",
    "obtener_permisos_frontend",
    "ACCESS_TOKEN_EXPIRE_MINUTES"
]