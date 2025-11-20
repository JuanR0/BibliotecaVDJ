from config.database import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS PRINCIPALES
# =============================================

class Libro(Base):
    __tablename__ = "libros"
    
    id = Column(Integer, primary_key=True, index=True)
    # Identificación física
    codigo_decimal = Column(String(20), nullable=False)
    etiqueta = Column(String(3), nullable=False)
    numero_ejemplar = Column(Integer, nullable=False)
    # Metadatos del libro
    isbn = Column(String(20))
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    editorial_id = Column(Integer, ForeignKey("editoriales.id"), nullable=False)
    edicion = Column(Integer)  # ← Cambiado a Integer
    numero_paginas = Column(Integer)
    area_conocimiento_id = Column(Integer, ForeignKey("areas_conocimiento.id"), nullable=False)
    # Información de adquisición
    fecha_adquisicion = Column(TIMESTAMP, server_default=func.now())
    metodo_adquisicion_id = Column(Integer, ForeignKey("metodos_adquisicion.id"), nullable=False)  # ← Cambiado a FK
    proveedor_nombre = Column(String(255))
    precio = Column(DECIMAL(10, 2))
    es_prestable = Column(Boolean, default=True)
    # Seguimiento y estado
    usuario_registro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados_libro.id"), nullable=False)
    fecha_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    editorial = relationship("Editorial", back_populates="libros")
    area_conocimiento = relationship("AreaConocimiento", back_populates="libros")
    usuario_registro = relationship("Usuario", back_populates="libros_registrados")
    estado = relationship("EstadoLibro", back_populates="libros")
    metodo_adquisicion = relationship("MetodoAdquisicion", back_populates="libros")  # ← Nueva relación