from config.database import Base  # ← Con punto
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS PRINCIPALES
# =============================================

class EquipoComputo(Base):
    __tablename__ = "equipos_computo"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String(50), unique=True, nullable=False)
    marca_id = Column(Integer, ForeignKey("marcas_equipo_computo.id"), nullable=False)
    modelo = Column(String(50), nullable=False)
    tipo_equipo_id = Column(Integer, ForeignKey("tipos_equipo_computo.id"), nullable=False)
    especificaciones = Column(Text)
    es_prestable = Column(Boolean, default=True)
    usuario_registro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados_equipo.id"), nullable=False)
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    marca_equipo = relationship("MarcaEquipoComputo", back_populates="equipos_computo")
    tipo_equipo = relationship("TipoEquipoComputo", back_populates="equipos_computo")
    usuario_registro = relationship("Usuario", back_populates="equipos_registrados")
    area = relationship("Area", back_populates="equipos_computo")
    estado = relationship("EstadoEquipo", back_populates="equipos_computo")