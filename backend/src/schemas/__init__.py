# Re-exportar todos los schemas para fácil importación

from .auth import UsuarioLogin, Token, TokenData
from .users import (
    # Schemas base y creación
    UsuarioBase,
    UsuarioCreate,
    UsuarioCreateAdmin,
    
    # Schemas de actualización
    UsuarioUpdate,
    UsuarioUpdateSelf,
    PasswordChange,
    
    # Schemas de respuesta
    UsuarioResponse,
    UsuarioDetailResponse,
    UsuarioSearchResponse,
    UsuarioListResponse,
    UsuarioConRelacionesResponse,
    
    # Schemas de estado
    UsuarioStatusChange,
    
    # Schemas para relaciones (nuevos)
    TipoUsuarioSimple,
    RelacionInstitucionalSimple
)

# Para errores y comunes
from pydantic import BaseModel
from typing import List, Optional

class ErrorResponse(BaseModel):
    """Esquema para respuestas de error"""
    detail: str
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Esquema para errores de validación"""
    detail: List[dict]

# Enums comunes
from enum import Enum

class TipoUsuarioEnum(str, Enum):
    comun = "Comun"
    admin = "Admin" 
    super_admin = "SuperAdmin"

class RelacionInstitucionalEnum(str, Enum):
    estudiante = "Estudiante"
    academico = "Academico"
    administrativo = "Administrativo"
    otro = "Otro"

class EstadoUsuarioEnum(str, Enum):
    activo = "activo"
    inactivo = "inactivo"

# Exportar todo
__all__ = [
    # Auth
    "UsuarioLogin", "Token", "TokenData",
    
    # Users - Principales
    "UsuarioBase", "UsuarioCreate", "UsuarioCreateAdmin", 
    "UsuarioUpdate", "UsuarioUpdateSelf", "PasswordChange",
    "UsuarioResponse", "UsuarioDetailResponse", "UsuarioSearchResponse",
    "UsuarioListResponse", "UsuarioStatusChange",
    
    # Users - Relaciones anidadas (nuevos)
    "TipoUsuarioSimple", "RelacionInstitucionalSimple", "UsuarioConRelacionesResponse",
    
    # Commons
    "ErrorResponse", "ValidationErrorResponse",
    "TipoUsuarioEnum", "RelacionInstitucionalEnum", "EstadoUsuarioEnum"
]