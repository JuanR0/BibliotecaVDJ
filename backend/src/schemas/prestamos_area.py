from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta
from typing import Optional

# Schema base común
class PrestamoAreaBase(BaseModel):
    area_id: int
    usuario_prestado_id: int
    fecha_devolucion_esperada: datetime
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para crear préstamo (POST) - SIN ID
class PrestamoAreaCreate(PrestamoAreaBase):
    # No incluimos campos que se generan automáticamente
    pass

    # @field_validator('fecha_devolucion_esperada')
    # @classmethod
    # def fecha_devolucion_debe_ser_futura(cls, v):
    #     if v <= datetime.now():
    #         raise ValueError('La fecha de devolución debe ser futura')
    #     return v

    # @field_validator('fecha_devolucion_esperada')
    # @classmethod
    # def validar_duracion_prestamo(cls, v):
    #     # Validar que el préstamo no exceda las 8 horas (por ejemplo)
    #     duracion_maxima = timedelta(hours=8)
    #     ahora = datetime.now()
    #     if v - ahora > duracion_maxima:
    #         raise ValueError('El préstamo no puede exceder las 8 horas')
    #     return v

# Schema para respuesta (GET) - CON ID
class PrestamoAreaResponse(PrestamoAreaBase):
    id: int
    usuario_presta_id: int
    estado_prestamo_id: int
    fecha_prestamo: datetime
    fecha_devolucion_esperada: datetime
    fecha_devolucion_real: Optional[datetime] = None
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    tiempo_excedido: Optional[timedelta] = None
    horas_excedidas: float = 0.0  # Campo calculado para facilitar el frontend

    class Config:
        from_attributes = True

    @field_validator('horas_excedidas', mode='before')
    @classmethod
    def calcular_horas_excedidas(cls, v, info):
        # Calcular horas excedidas a partir del tiempo_excedido
        if 'tiempo_excedido' in info.data and info.data['tiempo_excedido']:
            tiempo_excedido = info.data['tiempo_excedido']
            if isinstance(tiempo_excedido, timedelta):
                return round(tiempo_excedido.total_seconds() / 3600, 2)
        return 0.0

# Schema para respuesta con datos relacionados
class PrestamoAreaConRelaciones(BaseModel):
    id: int
    area_id: int
    usuario_presta_id: int
    usuario_prestado_id: int
    estado_prestamo_id: int
    fecha_prestamo: datetime
    fecha_devolucion_esperada: datetime
    fecha_devolucion_real: Optional[datetime] = None
    usuario_ultimo_cambio_id: Optional[int] = None
    fecha_ultimo_cambio_estado: Optional[datetime] = None
    observaciones: Optional[str] = None
    tiempo_excedido: Optional[timedelta] = None
    horas_excedidas: float = 0.0
    
    # Campos relacionados
    area_nombre: Optional[str] = None
    area_capacidad: Optional[int] = None
    usuario_presta_nombre: Optional[str] = None
    usuario_prestado_nombre: Optional[str] = None
    usuario_ultimo_cambio_nombre: Optional[str] = None
    estado_prestamo_nombre: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator('horas_excedidas', mode='before')
    @classmethod
    def calcular_horas_excedidas(cls, v, info):
        # Calcular horas excedidas a partir del tiempo_excedido
        if 'tiempo_excedido' in info.data and info.data['tiempo_excedido']:
            tiempo_excedido = info.data['tiempo_excedido']
            if isinstance(tiempo_excedido, timedelta):
                return round(tiempo_excedido.total_seconds() / 3600, 2)
        return 0.0

# Schema para actualizar préstamo (PUT/PATCH)
class PrestamoAreaUpdate(BaseModel):
    estado_prestamo_id: Optional[int] = None
    fecha_devolucion_real: Optional[datetime] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para devolución de área
class PrestamoAreaDevolucion(BaseModel):
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para estadísticas o reportes
class PrestamoAreaEstadisticas(BaseModel):
    area_id: int
    area_nombre: str
    total_prestamos: int
    prestamos_vigentes: int
    tiempo_promedio_excedido: Optional[timedelta] = None
    horas_promedio_excedidas: float = 0.0

    class Config:
        from_attributes = True