from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class PrestamoEquipoComputo(Base):
    __tablename__ = "prestamos_equipo_computo"
    
    # ID principal
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones principales
    equipos_computo_id = Column(Integer, ForeignKey("equipos_computo.id"), nullable=False)
    usuario_presta_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_prestado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado_prestamo_id = Column(Integer, ForeignKey("estados_prestamo.id"), nullable=False)
    
    # Fechas del ciclo de préstamo (DIFERENCIA CLAVE)
    fecha_prestamo = Column(DateTime, nullable=False, server_default=func.now())
    # NO existe fecha_devolucion_esperada - el equipo no sale de la biblioteca
    fecha_devolucion = Column(DateTime)  # Solo cuando realmente se devuelve
    
    # Auditoría
    usuario_ultimo_cambio_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_ultimo_cambio_estado = Column(DateTime, server_default=func.now())
    
    # Observaciones
    observaciones = Column(Text)
    # NO existe dias_excedidos - no hay concepto de excedente

    # Relaciones
    equipo_computo = relationship("EquipoComputo", back_populates="prestamos_equipo_computo")
    
    # Usuario que realiza el préstamo (bibliotecario)
    usuario_presta = relationship(
        "Usuario", 
        foreign_keys=[usuario_presta_id],
        back_populates="prestamos_equipo_realizados"
    )
    
    # Usuario que recibe el préstamo (estudiante/profesor)
    usuario_prestado = relationship(
        "Usuario", 
        foreign_keys=[usuario_prestado_id],
        back_populates="prestamos_equipo_recibidos"
    )
    
    # Estado del préstamo
    estado_prestamo = relationship("EstadoPrestamo", back_populates="prestamos_equipo_computo")
    
    # Usuario que hizo el último cambio de estado
    usuario_ultimo_cambio = relationship(
        "Usuario", 
        foreign_keys=[usuario_ultimo_cambio_id],
        back_populates="cambios_estado_prestamos_equipo"
    )