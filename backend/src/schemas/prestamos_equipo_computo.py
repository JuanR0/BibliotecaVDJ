from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

# Schema base común
class PrestamoEquipoComputoBase(BaseModel):
    equipos_computo_id: int
    usuario_prestado_id: int
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema para crear préstamo (POST) - SIN ID
class PrestamoEquipoComputoCreate(PrestamoEquipoComputoBase):
    # No incluimos campos que se generan automáticamente
    # DIFERENCIA: No tiene fecha_devolucion_esperada
    pass

# Schema para respuesta (GET) - CON ID
class PrestamoEquipoComputoResponse(PrestamoEquipoComputoBase):
    id: int
    usuario_presta_id: int
    estado_prestamo_id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None  # Original, no _real
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    # DIFERENCIA: No tiene dias_excedidos
    
    class Config:
        from_attributes = True

# Schema para respuesta con datos relacionados
class PrestamoEquipoComputoConRelaciones(BaseModel):
    id: int
    equipos_computo_id: int
    usuario_presta_id: int
    usuario_prestado_id: int
    estado_prestamo_id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None  # Original, no _real
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    observaciones: Optional[str] = None
    # DIFERENCIA: No tiene dias_excedidos
    
    # Campos relacionados
    equipo_numero_serie: Optional[str] = None
    equipo_marca: Optional[str] = None
    equipo_modelo: Optional[str] = None
    equipo_tipo: Optional[str] = None
    usuario_presta_nombre: Optional[str] = None
    usuario_prestado_nombre: Optional[str] = None
    estado_prestamo_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema para actualizar préstamo (PUT/PATCH)
class PrestamoEquipoComputoUpdate(BaseModel):
    estado_prestamo_id: Optional[int] = None
    fecha_devolucion: Optional[datetime] = None  # Original, no _real
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema para devolución de equipo
class PrestamoEquipoComputoDevolucion(BaseModel):
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True  