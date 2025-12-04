from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class PrestamoLibro(Base):
    __tablename__ = "prestamos_libro"
    
    # ID principal
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones principales
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    usuario_presta_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_prestado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado_prestamo_id = Column(Integer, ForeignKey("estados_prestamo.id"), nullable=False)
    
    # Fechas del ciclo de préstamo
    fecha_prestamo = Column(DateTime, nullable=False, server_default=func.now())
    fecha_devolucion_esperada = Column(DateTime, nullable=False)
    fecha_devolucion_real = Column(DateTime)
    
    # Auditoría
    usuario_ultimo_cambio_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_ultimo_cambio_estado = Column(DateTime, server_default=func.now())
    
    # Observaciones
    observaciones = Column(Text)
    dias_excedidos = Column(Integer, default=0)

    # Relaciones
    libro = relationship("Libro", back_populates="prestamos")
    usuario_presta = relationship("Usuario", foreign_keys=[usuario_presta_id], back_populates="prestamos_realizados")
    usuario_prestado = relationship("Usuario", foreign_keys=[usuario_prestado_id], back_populates="prestamos_recibidos")
    estado_prestamo = relationship("EstadoPrestamo", back_populates="prestamos")  
    usuario_ultimo_cambio = relationship("Usuario", foreign_keys=[usuario_ultimo_cambio_id], back_populates="cambios_estado_prestamos")