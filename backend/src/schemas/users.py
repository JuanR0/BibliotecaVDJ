from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UsuarioBase(BaseModel):
    """Esquema base para usuario"""
    codigo_universitario: str = Field(..., min_length=1, max_length=20)
    nombre_completo: str = Field(..., min_length=1, max_length=255)

    @field_validator('nombre_completo')
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El nombre completo no puede estar vacío')
        return v.strip()

    @field_validator('codigo_universitario')
    @classmethod
    def codigo_formato_valido(cls, v: str) -> str:
        if len(v) > 20:
            raise ValueError('El código universitario no puede exceder 20 caracteres')
        return v

class UsuarioCreate(UsuarioBase):
    """Esquema para crear nuevo usuario"""
    clave_acceso: str = Field(..., min_length=6, max_length=72)  # ✅ Límite real de bcrypt
    relacion_institucional_id: int = Field(..., gt=0)
    tipo_usuario_id: int = Field(..., gt=0)
    usuario_creador_id: Optional[int] = Field(None, gt=0)
    
    @field_validator('clave_acceso')
    @classmethod
    def clave_longitud_valida(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('La clave debe tener al menos 6 caracteres')
        if len(v.encode('utf-8')) > 72:  # ✅ Validar por BYTES, no caracteres
            raise ValueError('La clave es demasiado larga (máximo 72 bytes)')
        return v

class UsuarioCreateAdmin(UsuarioCreate):
    """Esquema para crear usuario (solo administradores)"""
    pass

class UsuarioUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    relacion_institucional_id: Optional[int] = Field(None, gt=0)
    tipo_usuario_id: Optional[int] = Field(None, gt=0)
    esta_activo: Optional[bool] = None

    @field_validator('nombre_completo')
    @classmethod
    def nombre_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else v

class UsuarioUpdateSelf(BaseModel):
    """Esquema para que usuario actualice sus propios datos"""
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)

    @field_validator('nombre_completo')
    @classmethod
    def nombre_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else v

class PasswordChange(BaseModel):
    """Esquema para cambiar contraseña"""
    clave_actual: str = Field(..., min_length=1)
    clave_nueva: str = Field(..., min_length=6)

    @field_validator('clave_nueva')
    @classmethod
    def clave_nueva_valida(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('La nueva clave debe tener al menos 6 caracteres')
        return v

class UsuarioResponse(UsuarioBase):
    """Esquema para respuesta de usuario (sin info sensible)"""
    id: int
    relacion_institucional_id: int
    tipo_usuario_id: int
    esta_activo: bool
    fecha_registro: datetime
    fecha_ultimo_cambio_estado: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class UsuarioDetailResponse(UsuarioResponse):
    """Esquema con detalles extendidos del usuario"""
    # NOTA: Para usar este schema, necesitarás cargar las relaciones
    # con joinedload() en el endpoint y construir manualmente o usar
    # propiedades en el modelo para los nombres
    usuario_creador_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class UsuarioSearchResponse(BaseModel):
    """Esquema para búsqueda de usuarios (solo campos existentes)"""
    id: int
    codigo_universitario: str
    nombre_completo: str
    relacion_institucional_id: int  # ✅ Campo que existe en el modelo
    tipo_usuario_id: int            # ✅ Campo que existe en el modelo
    esta_activo: bool

    model_config = {
        "from_attributes": True  # ✅ Ahora SÍ funciona
    }

class UsuarioListResponse(BaseModel):
    """Esquema para listado de usuarios"""
    usuarios: List[UsuarioResponse]  # ✅ Usa UsuarioResponse que tiene campos existentes
    total: int
    pagina: int
    por_pagina: int

class UsuarioStatusChange(BaseModel):
    """Esquema para cambiar estado de usuario"""
    esta_activo: bool
    # motivo: Optional[str] = Field(None, max_length=500)  # ⚠️ Comentado por ahora

# Schemas para relaciones (opcionales - para cuando quieras nested objects)
class TipoUsuarioSimple(BaseModel):
    """Esquema simple para tipo de usuario (para relaciones anidadas)"""
    id: int
    tipo: str
    descripcion: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class RelacionInstitucionalSimple(BaseModel):
    """Esquema simple para relación institucional (para relaciones anidadas)"""
    id: int
    relacion: str
    descripcion: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class UsuarioConRelacionesResponse(BaseModel):
    """Esquema para usuario con relaciones anidadas (para endpoints detallados)"""
    id: int
    codigo_universitario: str
    nombre_completo: str
    relacion_institucional_id: int
    tipo_usuario_id: int
    esta_activo: bool
    fecha_registro: datetime
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    # Relaciones anidadas (opcionales - requieren joinedload en el endpoint)
    relacion_institucional: Optional[RelacionInstitucionalSimple] = None
    tipo_usuario: Optional[TipoUsuarioSimple] = None

    model_config = {
        "from_attributes": True
    }

class UsuarioRegister(UsuarioBase):
        """Esquema para registro público - sin tipo_usuario_id"""
        clave_acceso: str = Field(..., min_length=6, max_length=72)
        relacion_institucional_id: int = Field(..., gt=0)
        # ✅ NO incluye tipo_usuario_id - siempre será usuario común
        
        @field_validator('clave_acceso')
        @classmethod
        def clave_longitud_valida(cls, v: str) -> str:
            if len(v) < 6:
                raise ValueError('La clave debe tener al menos 6 caracteres')
            if len(v.encode('utf-8')) > 72:
                raise ValueError('La clave es demasiado larga (máximo 72 bytes)')
            return v