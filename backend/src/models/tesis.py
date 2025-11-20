from config.database import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS PRINCIPALES
# =============================================

class Tesis(Base):
    __tablename__ = "tesis"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_decimal = Column(String(20), unique=True, nullable=False)
    titulo = Column(String(500), nullable=False)
    numero_paginas = Column(Integer)
    fecha_publicacion = Column(String(50), nullable=False)
    # Información del autor
    nombre_autor = Column(String(255), nullable=False)
    codigo_universitario_autor = Column(String(20), nullable=False)
    generacion = Column(String(10))
    carrera = Column(String(100), nullable=False)
    nivel_estudios_id = Column(Integer, ForeignKey("niveles_estudio.id"), nullable=False)  # ← Cambiado
    # Fisico
    usuario_ingreso_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_ingreso = Column(TIMESTAMP, server_default=func.now())
    estado_fisico_id = Column(Integer, ForeignKey("estados_libro.id"), nullable=False)
    fecha_ultimo_cambio_estado_fisico = Column(TIMESTAMP, server_default=func.now())
    # Virtual
    usuario_subio_virtual_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_subida_virtual = Column(TIMESTAMP)
    link_copia_virtual = Column(String(255))
    estado_virtual_id = Column(Integer, ForeignKey("estados_virtual.id"), nullable=False)
    fecha_ultimo_cambio_estado_virtual = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    usuario_ingreso = relationship("Usuario", back_populates="tesis_ingresadas", foreign_keys=[usuario_ingreso_id])
    usuario_subio_virtual = relationship("Usuario", back_populates="tesis_subidas_virtual", foreign_keys=[usuario_subio_virtual_id])
    estado_fisico = relationship("EstadoLibro", foreign_keys=[estado_fisico_id])
    estado_virtual = relationship("EstadoVirtual", back_populates="tesis_estado_virtual", foreign_keys=[estado_virtual_id])
    nivel_estudio = relationship("NivelEstudio", back_populates="tesis")  # ← Nueva relación