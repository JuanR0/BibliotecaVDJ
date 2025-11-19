from config.database import Base  # ← Con punto
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Area(Base):
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    capacidad = Column(Integer)
    es_prestable = Column(Boolean, default=False)
    usuario_registro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    estado_id = Column(Integer, ForeignKey("estados_area.id"), nullable=False)
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    usuario_registro = relationship("Usuario", back_populates="areas_creadas")
    estado = relationship("EstadoArea", back_populates="areas")
    equipos_computo = relationship("EquipoComputo", back_populates="area")
    mobiliarios = relationship("Mobiliario", back_populates="area")