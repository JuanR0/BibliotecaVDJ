# src/schemas/areas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class AreaBase(BaseModel):
    """Esquema base para área"""
    nombre: str = Field(..., min_length=1, max_length=100)
    capacidad: Optional[int] = Field(None, ge=1)
    es_prestable: bool = False
    estado_id: int = Field(..., ge=1, le=5)  # Ya incluye el estado 5

    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

class AreaCreate(AreaBase):
    """Esquema para crear nueva área"""
    pass

class AreaUpdate(BaseModel):
    """Esquema para actualizar área"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    capacidad: Optional[int] = Field(None, ge=1)
    es_prestable: Optional[bool] = None
    estado_id: Optional[int] = Field(None, ge=1, le=4)  # No permite estado 5 en update

    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else v

class AreaResponse(AreaBase):
    """Esquema para respuesta de área"""
    id: int
    usuario_registro_id: int
    fecha_registro: datetime
    fecha_ultimo_cambio_estado: datetime

    model_config = {
        "from_attributes": True
    }

class AreaConRelacionesResponse(AreaResponse):
    """Esquema para área con relaciones anidadas"""
    estado_nombre: Optional[str] = None
    usuario_registro_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class AreaListResponse(BaseModel):
    """Esquema para listado de áreas"""
    areas: List[AreaConRelacionesResponse]
    total: int
    pagina: int
    por_pagina: int

class AreaSearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de áreas"""
    nombre: Optional[str] = None
    estado_id: Optional[int] = None
    es_prestable: Optional[bool] = None
    incluir_eliminadas: Optional[bool] = False

# Schemas para las tablas auxiliares
class EstadoAreaResponse(BaseModel):
    id: int
    estado: str

    model_config = {
        "from_attributes": True
    }