from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class LibroVirtualBase(BaseModel):
    """Esquema base para libro virtual"""
    isbn: Optional[str] = Field(None, max_length=20)
    titulo: str = Field(..., min_length=1, max_length=255)
    autor: str = Field(..., min_length=1, max_length=255)
    editorial_id: int = Field(..., gt=0)
    edicion: Optional[int] = Field(None, gt=0)
    numero_paginas: Optional[int] = Field(None, ge=1)
    area_conocimiento_id: int = Field(..., gt=0)
    archivo_digital: str = Field(..., min_length=1, max_length=255, description="URL o path del archivo digital")
    estado_virtual_id: int = Field(..., gt=0)

    @field_validator('titulo')
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

    @field_validator('autor')
    @classmethod
    def autor_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El autor no puede estar vacío')
        return v.strip()

    @field_validator('archivo_digital')
    @classmethod
    def archivo_valido(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El archivo digital no puede estar vacío')
        return v.strip()

class LibroVirtualCreate(LibroVirtualBase):
    """Esquema para crear libro virtual"""
    pass

class LibroVirtualUpdate(BaseModel):
    """Esquema para actualizar libro virtual"""
    isbn: Optional[str] = Field(None, max_length=20)
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    autor: Optional[str] = Field(None, min_length=1, max_length=255)
    editorial_id: Optional[int] = Field(None, gt=0)
    edicion: Optional[int] = Field(None, gt=0)
    numero_paginas: Optional[int] = Field(None, ge=1)
    area_conocimiento_id: Optional[int] = Field(None, gt=0)
    archivo_digital: Optional[str] = Field(None, min_length=1, max_length=255)
    estado_virtual_id: Optional[int] = Field(None, gt=0)

    @field_validator('titulo')
    @classmethod
    def titulo_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip() if v else v

    @field_validator('autor')
    @classmethod
    def autor_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El autor no puede estar vacío')
        return v.strip() if v else v

    @field_validator('archivo_digital')
    @classmethod
    def archivo_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El archivo digital no puede estar vacío')
        return v.strip() if v else v

class LibroVirtualResponse(LibroVirtualBase):
    """Esquema para respuesta de libro virtual"""
    id: int
    usuario_subio_id: int
    fecha_creacion: datetime
    fecha_ultimo_cambio_estado: datetime

    model_config = {
        "from_attributes": True
    }

class LibroVirtualConRelacionesResponse(LibroVirtualResponse):
    """Esquema para libro virtual con relaciones"""
    editorial_nombre: Optional[str] = None
    area_conocimiento_nombre: Optional[str] = None
    estado_virtual_nombre: Optional[str] = None
    usuario_subio_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class LibroVirtualListResponse(BaseModel):
    """Esquema para listado de libros virtuales"""
    libros_virtuales: List[LibroVirtualConRelacionesResponse]
    total: int
    pagina: int
    por_pagina: int

class LibroVirtualSearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de libros virtuales"""
    titulo: Optional[str] = None
    autor: Optional[str] = None
    editorial_id: Optional[int] = None
    area_conocimiento_id: Optional[int] = None
    estado_virtual_id: Optional[int] = None

# Schemas para tablas auxiliares
class EstadoVirtualResponse(BaseModel):
    id: int
    estado: str

    model_config = {
        "from_attributes": True
    }

class EditorialResponse(BaseModel):
    id: int
    nombre: str

    model_config = {
        "from_attributes": True
    }

class AreaConocimientoResponse(BaseModel):
    id: int
    nombre: str
    rango_inicio: str
    rango_fin: str

    model_config = {
        "from_attributes": True
    }