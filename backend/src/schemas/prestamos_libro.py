from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# =============================================
# SCHEMAS BASE
# =============================================

class PrestamoLibroBase(BaseModel):
    libro_id: int
    usuario_prestado_id: int
    fecha_devolucion_esperada: datetime
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

class PrestamoLibroCreate(PrestamoLibroBase):
    pass

    # Validador descomentado — rechaza fechas en el pasado desde el backend también
    @field_validator('fecha_devolucion_esperada')
    @classmethod
    def fecha_devolucion_debe_ser_futura(cls, v):
        # Comparar solo fechas (ignorar horas) para permitir "hoy"
        fecha_naive = v.replace(tzinfo=None) if v.tzinfo else v
        hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if fecha_naive < hoy:
            raise ValueError('La fecha de devolución no puede ser anterior a hoy')
        return v

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

class PrestamoLibroUpdate(BaseModel):
    estado_prestamo_id: Optional[int] = None
    fecha_devolucion_real: Optional[datetime] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

class PrestamoLibroDevolucion(BaseModel):
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================
# NUEVO: Schema para respuesta de devolución
# Incluye la multa generada si el préstamo estaba vencido
# =============================================
 
class SolicitudDevolucionResponse(BaseModel):
    """
    Respuesta cuando el usuario solicita la devolución.
    Contiene el número de ticket para presentar en el CID.
    Formato del ticket: YYYYMMDDHHMMSS + id (ej: 20260425143022015)
    """
    prestamo_id: int
    numero_ticket: int
    fecha_solicitud: datetime
    libro_titulo: Optional[str] = None
    mensaje: str
 
    class Config:
        from_attributes = True
 
class AprobacionDevolucionRequest(BaseModel):
    observaciones: Optional[str] = None
 
    class Config:
        from_attributes = True

class MultaResumenEnDevolucion(BaseModel):
    """Resumen de la multa generada al devolver un libro vencido"""
    id: int
    costo_monetario: Decimal
    dias_excedidos: int
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: str(v)}


class PrestamoDevolucionResponse(BaseModel):
    """
    Respuesta del endpoint PATCH /devolver
    Siempre incluye el préstamo actualizado.
    Si hubo días excedidos, incluye también la multa generada.
    """
    prestamo: PrestamoLibroResponse
    multa_generada: Optional[MultaResumenEnDevolucion] = None
    mensaje: str

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: str(v)}