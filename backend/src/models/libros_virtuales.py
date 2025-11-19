from config.database import Base  # ← Con punto
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS PRINCIPALES
# =============================================

class LibroVirtual(Base):
    __tablename__ = "libros_virtuales"
    
    id = Column(Integer, primary_key=True, index=True)
    # Metadatos del libro
    isbn = Column(String(20))
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    editorial_id = Column(Integer, ForeignKey("editoriales.id"), nullable=False)
    edicion = Column(String(50))
    numero_paginas = Column(Integer)
    area_conocimiento_id = Column(Integer, ForeignKey("areas_conocimiento.id"), nullable=False)
    # Relevante a lo digital
    archivo_digital = Column(String(255), nullable=False)
    usuario_subio_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    estado_virtual_id = Column(Integer, ForeignKey("estados_virtual.id"), nullable=False)
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones SIN lazy="selectin" (como Libro)
    editorial = relationship("Editorial")
    area_conocimiento = relationship("AreaConocimiento")
    estado_virtual = relationship("EstadoVirtual", back_populates="libros_virtuales")
    usuario_subio = relationship("Usuario", back_populates="libros_virtuales_subidos")