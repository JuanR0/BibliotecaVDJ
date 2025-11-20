from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class LibroBase(BaseModel):
    """Esquema base para libro"""
    codigo_decimal: str = Field(..., min_length=1, max_length=20)
    etiqueta: str = Field(..., min_length=3, max_length=3)
    numero_ejemplar: int = Field(..., ge=1)
    isbn: Optional[str] = Field(None, max_length=20)
    titulo: str = Field(..., min_length=1, max_length=255)
    autor: str = Field(..., min_length=1, max_length=255)
    editorial_id: int = Field(..., gt=0)
    edicion: Optional[int] = Field(None, ge=1)  # ← Cambiado a int
    numero_paginas: Optional[int] = Field(None, ge=1)
    area_conocimiento_id: int = Field(..., gt=0)
    metodo_adquisicion_id: int = Field(..., gt=0, description="ID del método de adquisición (1: Compra, 2: Donacion)")  # ← Cambiado
    proveedor_nombre: Optional[str] = Field(None, max_length=255)
    precio: Optional[Decimal] = Field(None, ge=0)
    es_prestable: bool = True
    estado_id: int = Field(..., gt=0)

    @field_validator('etiqueta')
    @classmethod
    def etiqueta_exactamente_3_chars(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError('La etiqueta debe tener exactamente 3 caracteres')
        return v.upper()

    @field_validator('codigo_decimal')
    @classmethod
    def codigo_decimal_valido(cls, v: str) -> str:
        # Validación básica - luego validaremos contra el área de conocimiento
        if not v.replace('.', '').isdigit():
            raise ValueError('El código decimal debe contener solo números y puntos')
        return v

class LibroCreate(LibroBase):
    """Esquema para crear nuevo libro"""
    pass

class LibroUpdate(BaseModel):
    """Esquema para actualizar libro"""
    isbn: Optional[str] = Field(None, max_length=20)
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    autor: Optional[str] = Field(None, min_length=1, max_length=255)
    editorial_id: Optional[int] = Field(None, gt=0)
    edicion: Optional[int] = Field(None, ge=1)  # ← Cambiado a int
    numero_paginas: Optional[int] = Field(None, ge=1)
    metodo_adquisicion_id: Optional[int] = Field(None, gt=0)  # ← Cambiado
    proveedor_nombre: Optional[str] = Field(None, max_length=255)
    precio: Optional[Decimal] = Field(None, ge=0)
    es_prestable: Optional[bool] = None
    estado_id: Optional[int] = Field(None, gt=0)

    @field_validator('titulo')
    @classmethod
    def titulo_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip() if v else v

class LibroResponse(LibroBase):
    """Esquema para respuesta de libro"""
    id: int
    fecha_adquisicion: datetime
    fecha_cambio_estado: datetime
    usuario_registro_id: int

    model_config = {
        "from_attributes": True
    }

class LibroConRelacionesResponse(LibroResponse):
    """Esquema para libro con relaciones anidadas"""
    editorial_nombre: Optional[str] = None
    area_conocimiento_nombre: Optional[str] = None
    estado_nombre: Optional[str] = None
    usuario_registro_nombre: Optional[str] = None
    metodo_adquisicion_nombre: Optional[str] = None  # ← Nuevo campo

    model_config = {
        "from_attributes": True
    }

class LibroListResponse(BaseModel):
    """Esquema para listado de libros"""
    libros: List[LibroConRelacionesResponse]
    total: int
    pagina: int
    por_pagina: int

class LibroSearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de libros"""
    titulo: Optional[str] = None
    autor: Optional[str] = None
    editorial_id: Optional[int] = None
    area_conocimiento_id: Optional[int] = None
    metodo_adquisicion_id: Optional[int] = None  # ← Cambiado
    estado_id: Optional[int] = None
    es_prestable: Optional[bool] = None
    codigo_decimal: Optional[str] = None

# Schemas para las tablas auxiliares
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

class EstadoLibroResponse(BaseModel):
    id: int
    estado: str

    model_config = {
        "from_attributes": True
    }

class MetodoAdquisicionResponse(BaseModel):  # ← Nuevo schema
    id: int
    tipo: str

    model_config = {
        "from_attributes": True
    }

class LibroCreateConEjemplares(BaseModel):
    """Esquema para crear múltiples ejemplares del mismo libro"""
    # Datos comunes a todos los ejemplares
    codigo_decimal: str = Field(..., min_length=1, max_length=20)
    etiqueta: str = Field(..., min_length=3, max_length=3)
    isbn: Optional[str] = Field(None, max_length=20)
    titulo: str = Field(..., min_length=1, max_length=255)
    autor: str = Field(..., min_length=1, max_length=255)
    editorial_id: int = Field(..., gt=0)
    edicion: Optional[int] = Field(None, ge=1)  # ← Cambiado a int
    numero_paginas: Optional[int] = Field(None, ge=1)
    area_conocimiento_id: int = Field(..., gt=0)
    metodo_adquisicion_id: int = Field(..., gt=0)  # ← Cambiado
    proveedor_nombre: Optional[str] = Field(None, max_length=255)
    precio: Optional[Decimal] = Field(None, ge=0)
    es_prestable: bool = True
    estado_id: int = Field(..., gt=0)
    
    # Información de ejemplares
    cantidad_ejemplares: int = Field(..., ge=1, le=100, description="Número de ejemplares a crear")
    numero_ejemplar_inicial: int = Field(1, ge=1, description="Número del primer ejemplar")

    @field_validator('etiqueta')
    @classmethod
    def etiqueta_exactamente_3_chars(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError('La etiqueta debe tener exactamente 3 caracteres')
        return v.upper()

    @field_validator('codigo_decimal')
    @classmethod
    def codigo_decimal_valido(cls, v: str) -> str:
        if not v.replace('.', '').isdigit():
            raise ValueError('El código decimal debe contener solo números y puntos')
        return v

    @field_validator('cantidad_ejemplares')
    @classmethod
    def cantidad_razonable(cls, v: int) -> int:
        if v > 50:
            raise ValueError('No se pueden crear más de 50 ejemplares a la vez')
        return v