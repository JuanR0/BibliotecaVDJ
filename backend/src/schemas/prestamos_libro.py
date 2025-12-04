from pydantic import BaseModel, validator, field_validator
from datetime import datetime
from typing import Optional, List

# Schema base común
class PrestamoLibroBase(BaseModel):
    libro_id: int
    usuario_prestado_id: int
    fecha_devolucion_esperada: datetime
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para crear préstamo (POST) - SIN ID
class PrestamoLibroCreate(PrestamoLibroBase):
    # No incluimos campos que se generan automáticamente
    pass

    # @field_validator('fecha_devolucion_esperada')
    # @classmethod
    # def fecha_devolucion_debe_ser_futura(cls, v):
    #     if v <= datetime.now():
    #         raise ValueError('La fecha de devolución debe ser futura')
    #     return v

# Schema para respuesta (GET) - CON ID (igual que LibroResponse)
class PrestamoLibroResponse(PrestamoLibroBase):
    id: int
    usuario_presta_id: int
    estado_prestamo_id: int
    fecha_prestamo: datetime
    fecha_devolucion_esperada: datetime
    fecha_devolucion_real: Optional[datetime] = None
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    dias_excedidos: int = 0  

    class Config:
        from_attributes = True

# Schema para respuesta con datos relacionados
class PrestamoLibroConRelaciones(BaseModel):
    id: int
    libro_id: int
    usuario_presta_id: int
    usuario_prestado_id: int
    estado_prestamo_id: int
    fecha_prestamo: datetime
    fecha_devolucion_esperada: datetime
    fecha_devolucion_real: Optional[datetime] = None
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    observaciones: Optional[str] = None
    dias_excedidos: int = 0 
    
    # Campos relacionados
    libro_titulo: Optional[str] = None
    libro_autor: Optional[str] = None
    libro_codigo_decimal: Optional[str] = None
    usuario_presta_nombre: Optional[str] = None
    usuario_prestado_nombre: Optional[str] = None
    estado_prestamo_nombre: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para actualizar préstamo (PUT/PATCH)
class PrestamoLibroUpdate(BaseModel):
    estado_prestamo_id: Optional[int] = None
    fecha_devolucion_real: Optional[datetime] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para devolución de libro
class PrestamoLibroDevolucion(BaseModel):
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True