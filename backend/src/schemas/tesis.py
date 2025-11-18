# src/schemas/tesis.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime

class TesisBase(BaseModel):
    """Esquema base para tesis"""
    codigo_decimal: str = Field(..., min_length=1, max_length=20)
    titulo: str = Field(..., min_length=1, max_length=500)
    numero_paginas: Optional[int] = Field(None, ge=1)
    fecha_publicacion: str = Field(..., description="Fecha en formato YYYY-MM-DD") 
    # Información del autor
    nombre_autor: str = Field(..., min_length=1, max_length=255)
    codigo_universitario_autor: str = Field(..., min_length=1, max_length=20)
    generacion: Optional[str] = Field(None, max_length=10)
    carrera: str = Field(..., min_length=1, max_length=100)
    nivel_estudios: str = Field(..., min_length=1, max_length=20)
    # Estados
    estado_fisico_id: int = Field(..., ge=1, le=4)  # 1-4 (estados_libro)
    estado_virtual_id: int = Field(..., ge=1, le=2)  # 1-2 (estados_virtual)

    @field_validator('fecha_publicacion')  # ✅ Nuevo validador para fecha
    @classmethod
    def validar_formato_fecha(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('La fecha de publicación no puede estar vacía')
        
        # Validar formato básico YYYY-MM-DD
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-11-18)')
        
        return v.strip()
    @field_validator('codigo_decimal')
    @classmethod
    def codigo_decimal_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El código decimal no puede estar vacío')
        return v.strip()

    @field_validator('titulo')
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

    @field_validator('nombre_autor')
    @classmethod
    def nombre_autor_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El nombre del autor no puede estar vacío')
        return v.strip()

class TesisCreate(TesisBase):
    """Esquema para crear nueva tesis"""
    pass

class TesisUpdate(BaseModel):
    """Esquema para actualizar tesis"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=500)
    numero_paginas: Optional[int] = Field(None, ge=1)
    fecha_publicacion: Optional[str] = Field(None, description="Fecha en formato YYYY-MM-DD")  # ✅ String
    nombre_autor: Optional[str] = Field(None, min_length=1, max_length=255)
    codigo_universitario_autor: Optional[str] = Field(None, min_length=1, max_length=20)
    generacion: Optional[str] = Field(None, max_length=10)
    carrera: Optional[str] = Field(None, min_length=1, max_length=100)
    nivel_estudios: Optional[str] = Field(None, min_length=1, max_length=20)
    estado_fisico_id: Optional[int] = Field(None, ge=1, le=4)
    estado_virtual_id: Optional[int] = Field(None, ge=1, le=2)
    link_copia_virtual: Optional[str] = Field(None, max_length=255)

    @field_validator('titulo')
    @classmethod
    def titulo_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip() if v else v

class TesisResponse(TesisBase):
    """Esquema para respuesta de tesis"""
    id: int
    usuario_ingreso_id: int
    fecha_ingreso: datetime
    fecha_ultimo_cambio_estado_fisico: datetime
    usuario_subio_virtual_id: Optional[int] = None
    fecha_subida_virtual: Optional[datetime] = None
    link_copia_virtual: Optional[str] = None
    fecha_ultimo_cambio_estado_virtual: datetime

    model_config = {
        "from_attributes": True
    }

class TesisConRelacionesResponse(TesisResponse):
    """Esquema para tesis con relaciones anidadas"""
    estado_fisico_nombre: Optional[str] = None
    estado_virtual_nombre: Optional[str] = None
    usuario_ingreso_nombre: Optional[str] = None
    usuario_subio_virtual_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class TesisListResponse(BaseModel):
    """Esquema para listado de tesis"""
    tesis: List[TesisConRelacionesResponse]
    total: int
    pagina: int
    por_pagina: int

class TesisSearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de tesis"""
    titulo: Optional[str] = None
    nombre_autor: Optional[str] = None
    carrera: Optional[str] = None
    codigo_decimal: Optional[str] = None
    estado_fisico_id: Optional[int] = None
    estado_virtual_id: Optional[int] = None

# Schemas para subida de archivo virtual
class TesisSubirVirtual(BaseModel):
    """Esquema para subir archivo virtual de tesis"""
    link_copia_virtual: str = Field(..., min_length=1, max_length=255)

    @field_validator('link_copia_virtual')
    @classmethod
    def link_valido(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El link de la copia virtual no puede estar vacío')
        return v.strip()