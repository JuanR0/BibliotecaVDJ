from config.database import Base
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class PrestamoArea(Base):
    __tablename__ = 'prestamos_area'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones principales
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    usuario_presta_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario_prestado_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    estado_prestamo_id = Column(Integer, ForeignKey('estados_prestamo.id'), nullable=False)
    usuario_ultimo_cambio_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Fechas del ciclo de préstamo
    fecha_prestamo = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_devolucion_esperada = Column(TIMESTAMP, nullable=False)
    fecha_devolucion_real = Column(TIMESTAMP)
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Tiempo excedido en la devolución
    tiempo_excedido = Column(Interval, default='0 seconds')
    
    # Observaciones
    observaciones = Column(Text)
    
    # Relaciones
    area = relationship("Area", back_populates="prestamos_areas")
    
    # Usuario que realiza el préstamo (bibliotecario)
    usuario_presta = relationship(
        "Usuario", 
        foreign_keys=[usuario_presta_id],
        back_populates="prestamos_areas_realizados"
    )
    
    # Usuario que recibe el préstamo (estudiante/profesor)
    usuario_prestado = relationship(
        "Usuario", 
        foreign_keys=[usuario_prestado_id],
        back_populates="prestamos_areas_recibidos"
    )
    
    # Usuario que realizó el último cambio
    usuario_ultimo_cambio = relationship(
        "Usuario", 
        foreign_keys=[usuario_ultimo_cambio_id],
        back_populates="cambios_estado_prestamos_areas"
    )
    
    # Estado del préstamo
    estado_prestamo = relationship("EstadoPrestamo", back_populates="prestamos_areas")