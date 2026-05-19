from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class PrestamoEquipoComputoBase(BaseModel):
    equipos_computo_id:  int
    usuario_prestado_id: int
    observaciones:       Optional[str] = None

    class Config:
        from_attributes = True

class PrestamoEquipoComputoCreate(PrestamoEquipoComputoBase):
    #FECHA PARA PRESTAMO CON HORAS
    fecha_devolucion: datetime

class PrestamoEquipoComputoResponse(PrestamoEquipoComputoBase):
    id:                         int
    usuario_presta_id:          int
    estado_prestamo_id:         int
    fecha_prestamo:             datetime
    fecha_devolucion:           Optional[datetime] = None
    usuario_ultimo_cambio_id:   Optional[int]      = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None

    class Config:
        from_attributes = True

class PrestamoEquipoComputoConRelaciones(BaseModel):
    id:                         int
    equipos_computo_id:         int
    usuario_presta_id:          int
    usuario_prestado_id:        int
    estado_prestamo_id:         int
    fecha_prestamo:             datetime
    fecha_devolucion:           Optional[datetime] = None
    usuario_ultimo_cambio_id:   Optional[int]      = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    observaciones:              Optional[str]      = None

    # Campos relacionados
    equipo_numero_serie:   Optional[str] = None
    equipo_marca:          Optional[str] = None
    equipo_modelo:         Optional[str] = None
    equipo_tipo:           Optional[str] = None
    usuario_presta_nombre:   Optional[str] = None
    usuario_prestado_nombre: Optional[str] = None
    estado_prestamo_nombre:  Optional[str] = None

    class Config:
        from_attributes = True

class PrestamoEquipoComputoUpdate(BaseModel):
    estado_prestamo_id: Optional[int]      = None
    fecha_devolucion:   Optional[datetime] = None
    observaciones:      Optional[str]      = None

    class Config:
        from_attributes = True

class PrestamoEquipoComputoDevolucion(BaseModel):
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True