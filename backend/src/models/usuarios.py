from config.database import Base  # ← Con punto
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS PRINCIPALES
# =============================================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_universitario = Column(String(20), unique=True, index=True, nullable=False)
    clave_acceso = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    relacion_institucional_id = Column(Integer, ForeignKey("relaciones_institucion.id"), nullable=False)
    tipo_usuario_id = Column(Integer, ForeignKey("tipos_usuario.id"), nullable=False)
    usuario_creador_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    esta_activo = Column(Boolean, default=True)
    fecha_ultimo_cambio_estado = Column(TIMESTAMP, server_default=func.now())
    
    # Relaciones
    relacion_institucional = relationship("RelacionInstitucional", back_populates="usuarios")
    tipo_usuario = relationship("TipoUsuario", back_populates="usuarios")
    # Relación recursiva (usuario que creó este usuario)
    creador = relationship("Usuario", remote_side=[id], backref="usuarios_creados")
    
    # Relaciones con otras tablas (como creador/registrador)
    areas_creadas = relationship("Area", back_populates="usuario_registro")
    libros_registrados = relationship("Libro", back_populates="usuario_registro")
    equipos_registrados = relationship("EquipoComputo", back_populates="usuario_registro")
    mobiliarios_creados = relationship("Mobiliario", back_populates="usuario_creador")
    libros_virtuales_subidos = relationship("LibroVirtual", back_populates="usuario_subio")
    tesis_ingresadas = relationship("Tesis", back_populates="usuario_ingreso", foreign_keys="[Tesis.usuario_ingreso_id]")
    tesis_subidas_virtual = relationship("Tesis", back_populates="usuario_subio_virtual", foreign_keys="[Tesis.usuario_subio_virtual_id]")
