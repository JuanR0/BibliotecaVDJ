# src/schemas/mobiliario.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class MobiliarioBase(BaseModel):
    """Esquema base para mobiliario"""
    tipo_mobiliario: str = Field(..., min_length=1, max_length=30)
    descripcion: Optional[str] = Field(None, max_length=255)
    area_id: int = Field(..., gt=0)
    estado_id: int = Field(..., gt=0)

    @field_validator('tipo_mobiliario')
    @classmethod
    def tipo_mobiliario_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El tipo de mobiliario no puede estar vacío')
        return v.strip()

class MobiliarioCreate(MobiliarioBase):
    """Esquema para crear nuevo mobiliario"""
    pass

class MobiliarioUpdate(BaseModel):
    """Esquema para actualizar mobiliario"""
    tipo_mobiliario: Optional[str] = Field(None, min_length=1, max_length=30)
    descripcion: Optional[str] = Field(None, max_length=255)
    area_id: Optional[int] = Field(None, gt=0)
    estado_id: Optional[int] = Field(None, gt=0)

    @field_validator('tipo_mobiliario')
    @classmethod
    def tipo_mobiliario_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El tipo de mobiliario no puede estar vacío')
        return v.strip() if v else v

class MobiliarioResponse(MobiliarioBase):
    """Esquema para respuesta de mobiliario"""
    id: int
    usuario_creador_id: int
    fecha_ingreso: datetime
    fecha_ultimo_cambio_estado: datetime

    model_config = {
        "from_attributes": True
    }

class MobiliarioConRelacionesResponse(MobiliarioResponse):
    """Esquema para mobiliario con relaciones anidadas"""
    area_nombre: Optional[str] = None
    estado_nombre: Optional[str] = None
    usuario_creador_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class MobiliarioListResponse(BaseModel):
    """Esquema para listado de mobiliario"""
    mobiliarios: List[MobiliarioConRelacionesResponse]
    total: int
    pagina: int
    por_pagina: int

class MobiliarioSearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de mobiliario"""
    tipo_mobiliario: Optional[str] = None
    area_id: Optional[int] = None
    estado_id: Optional[int] = None

# Schemas para las tablas auxiliares
class EstadoMobiliarioResponse(BaseModel):
    id: int
    estado: str

    model_config = {
        "from_attributes": True
    }