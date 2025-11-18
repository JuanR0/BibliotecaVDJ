# src/schemas/equipos_computo.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class EquipoComputoBase(BaseModel):
    """Esquema base para equipo de cómputo"""
    numero_serie: str = Field(..., min_length=1, max_length=50)
    marca_id: int = Field(..., gt=0)
    modelo: str = Field(..., min_length=1, max_length=50)
    tipo_equipo_id: int = Field(..., gt=0)
    especificaciones: Optional[str] = None
    es_prestable: bool = True
    area_id: int = Field(..., gt=0)
    estado_id: int = Field(..., gt=0)

    @field_validator('numero_serie')
    @classmethod
    def numero_serie_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El número de serie no puede estar vacío')
        return v.strip()

    @field_validator('modelo')
    @classmethod
    def modelo_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El modelo no puede estar vacío')
        return v.strip()

class EquipoComputoCreate(EquipoComputoBase):
    """Esquema para crear nuevo equipo de cómputo"""
    pass

class EquipoComputoUpdate(BaseModel):
    """Esquema para actualizar equipo de cómputo"""
    numero_serie: Optional[str] = Field(None, min_length=1, max_length=50)
    marca_id: Optional[int] = Field(None, gt=0)
    modelo: Optional[str] = Field(None, min_length=1, max_length=50)
    tipo_equipo_id: Optional[int] = Field(None, gt=0)
    especificaciones: Optional[str] = None
    es_prestable: Optional[bool] = None
    area_id: Optional[int] = Field(None, gt=0)
    estado_id: Optional[int] = Field(None, gt=0)

    @field_validator('numero_serie')
    @classmethod
    def numero_serie_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El número de serie no puede estar vacío')
        return v.strip() if v else v

    @field_validator('modelo')
    @classmethod
    def modelo_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El modelo no puede estar vacío')
        return v.strip() if v else v

class EquipoComputoResponse(EquipoComputoBase):
    """Esquema para respuesta de equipo de cómputo"""
    id: int
    usuario_registro_id: int
    fecha_registro: datetime
    fecha_ultimo_cambio_estado: datetime

    model_config = {
        "from_attributes": True
    }

class EquipoComputoConRelacionesResponse(EquipoComputoResponse):
    """Esquema para equipo de cómputo con relaciones anidadas"""
    marca_nombre: Optional[str] = None
    tipo_equipo_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    estado_nombre: Optional[str] = None
    usuario_registro_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class EquipoComputoListResponse(BaseModel):
    """Esquema para listado de equipos de cómputo"""
    equipos: List[EquipoComputoConRelacionesResponse]
    total: int
    pagina: int
    por_pagina: int

class EquipoComputoSearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de equipos de cómputo"""
    numero_serie: Optional[str] = None
    modelo: Optional[str] = None
    marca_id: Optional[int] = None
    tipo_equipo_id: Optional[int] = None
    area_id: Optional[int] = None
    estado_id: Optional[int] = None
    es_prestable: Optional[bool] = None

# Schemas para las tablas auxiliares
class MarcaEquipoComputoResponse(BaseModel):
    id: int
    marca: str

    model_config = {
        "from_attributes": True
    }

class TipoEquipoComputoResponse(BaseModel):
    id: int
    tipo: str

    model_config = {
        "from_attributes": True
    }

class EstadoEquipoResponse(BaseModel):
    id: int
    estado: str

    model_config = {
        "from_attributes": True
    }