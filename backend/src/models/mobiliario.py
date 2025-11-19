from config.database import Base  # ← Con punto
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS PRINCIPALES
# =============================================

class Mobiliario(Base):
    __tablename__ = "mobiliario"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_mobiliario = Column(String(30), nullable=False)
    descripcion = Column(String(255))
    fecha_ingreso = Column(TIMESTAMP, server_default=func.now())
    usuario_creador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados_mobiliario.id"), nullable=False)
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    usuario_creador = relationship("Usuario", back_populates="mobiliarios_creados")
    area = relationship("Area", back_populates="mobiliarios")
    estado = relationship("EstadoMobiliario", back_populates="mobiliarios")
