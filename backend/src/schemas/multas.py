from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# =============================================
# SCHEMAS BASE
# =============================================

# Schema base común
class MultaBase(BaseModel):
    usuario_multado_id: int
    tipo_pago_id: int
    tipo_recurso_multa_id: int
    costo_monetario: Decimal = Decimal('0.00')
    detalles_costo_en_especie: Optional[str] = None
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)  # Convierte Decimal a string para JSON
        }

# Schema para crear multa (POST) - SIN ID
class MultaCreate(MultaBase):
    # No incluimos campos que se generan automáticamente
    pass
    
    @field_validator('costo_monetario')
    @classmethod
    def costo_no_negativo(cls, v):
        if v < 0:
            raise ValueError('El costo monetario no puede ser negativo')
        return v

# Schema para respuesta (GET) - CON ID
class MultaResponse(MultaBase):
    id: int
    usuario_multa_id: int
    estado_multa_id: int
    fecha_multa: datetime
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }

# Schema para respuesta con datos relacionados
class MultaConRelaciones(BaseModel):
    id: int
    usuario_multa_id: int
    usuario_multado_id: int
    estado_multa_id: int
    fecha_multa: datetime
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    tipo_pago_id: int
    tipo_recurso_multa_id: int
    costo_monetario: Decimal
    detalles_costo_en_especie: Optional[str] = None
    observaciones: Optional[str] = None
    
    # Campos relacionados
    usuario_multa_nombre: Optional[str] = None
    usuario_multado_nombre: Optional[str] = None
    usuario_ultimo_cambio_nombre: Optional[str] = None
    estado_multa_nombre: Optional[str] = None
    tipo_pago_nombre: Optional[str] = None
    tipo_recurso_multa_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }

# =============================================
# SCHEMAS PARA ACTUALIZACIÓN
# =============================================

# Schema para actualizar multa (PUT/PATCH) - Campos editables
class MultaUpdate(BaseModel):
    estado_multa_id: Optional[int] = None
    tipo_pago_id: Optional[int] = None
    tipo_recurso_multa_id: Optional[int] = None
    costo_monetario: Optional[Decimal] = None
    detalles_costo_en_especie: Optional[str] = None
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }
    
    @field_validator('costo_monetario')
    @classmethod
    def costo_no_negativo(cls, v):
        if v is not None and v < 0:
            raise ValueError('El costo monetario no puede ser negativo')
        return v

# Schema para liquidar multa
class MultaLiquidacion(BaseModel):
    tipo_pago_id: Optional[int] = None  # Solo si cambia el tipo de pago
    costo_monetario: Optional[Decimal] = None  # Solo si ajusta el monto
    detalles_costo_en_especie: Optional[str] = None
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }

# Schema para cambiar estado específico
class MultaCambioEstado(BaseModel):
    estado_multa_id: int
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True

# =============================================
# SCHEMAS PARA FILTROS Y CONSULTAS
# =============================================

class FiltrosMulta(BaseModel):
    estado_multa_id: Optional[int] = None
    usuario_multado_id: Optional[int] = None
    tipo_pago_id: Optional[int] = None
    tipo_recurso_multa_id: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema para estadísticas/resumen
class ResumenMultas(BaseModel):
    total_multas: int
    multas_pendientes: int
    multas_liquidadas: int
    total_recaudado: Decimal
    por_tipo_recurso: List[dict]
    por_tipo_pago: List[dict]
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }