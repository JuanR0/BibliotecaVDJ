from config.database import Base  # ← Con punto
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text, DECIMAL, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# =============================================
# MODELOS DE TABLAS AUXILIARES (CATÁLOGOS)
# =============================================

class EstadoLibro(Base):
    __tablename__ = "estados_libro"
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relaciones
    libros = relationship("Libro", back_populates="estado")

class EstadoArea(Base):
    __tablename__ = "estados_area"
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relaciones
    areas = relationship("Area", back_populates="estado")

class EstadoEquipo(Base):
    __tablename__ = "estados_equipo"
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relaciones
    equipos_computo = relationship("EquipoComputo", back_populates="estado")

class EstadoMobiliario(Base):
    __tablename__ = "estados_mobiliario"
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relaciones
    mobiliarios = relationship("Mobiliario", back_populates="estado")

class EstadoMulta(Base):
    __tablename__ = "estados_multa"
    
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relación con multas
    multas = relationship("Multa", back_populates="estado_multa")

class EstadoPrestamo(Base):
    __tablename__ = "estados_prestamo"
    
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relación con préstamos libro
    prestamos = relationship("PrestamoLibro", back_populates="estado_prestamo")

    # Nueva relación con préstamos de áreas
    prestamos_areas = relationship("PrestamoArea", back_populates="estado_prestamo")

    prestamos_equipo_computo = relationship("PrestamoEquipoComputo", back_populates="estado_prestamo")

class EstadoVirtual(Base):
    __tablename__ = "estados_virtual"
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(20), unique=True, nullable=False)
    
    # Relaciones
    libros_virtuales = relationship("LibroVirtual", back_populates="estado_virtual")
    tesis_estado_virtual = relationship("Tesis", back_populates="estado_virtual", foreign_keys="[Tesis.estado_virtual_id]")

class Editorial(Base):
    __tablename__ = "editoriales"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    
    # Relaciones
    libros = relationship("Libro", back_populates="editorial")

class AreaConocimiento(Base):
    __tablename__ = "areas_conocimiento"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    rango_inicio = Column(String(20), nullable=False)
    rango_fin = Column(String(20), nullable=False)
    
    # Relaciones
    libros = relationship("Libro", back_populates="area_conocimiento")

class RelacionInstitucional(Base):
    __tablename__ = "relaciones_institucion"
    id = Column(Integer, primary_key=True, index=True)
    relacion = Column(String(20), unique=True, nullable=False)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="relacion_institucional")

class MarcaEquipoComputo(Base):
    __tablename__ = "marcas_equipo_computo"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(100), unique=True, nullable=False)
    
    # Relaciones
    equipos_computo = relationship("EquipoComputo", back_populates="marca_equipo")

class MetodoAdquisicion(Base):
    __tablename__ = "metodos_adquisicion"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(15), unique=True, nullable=False)
    
    # Relación con Libros
    libros = relationship("Libro", back_populates="metodo_adquisicion")

class NivelEstudio(Base):
    __tablename__ = "niveles_estudio"
    
    id = Column(Integer, primary_key=True, index=True)
    nivel = Column(String(100), unique=True, nullable=False)
    
    # Relación con Tesis
    tesis = relationship("Tesis", back_populates="nivel_estudio")

class TipoEquipoComputo(Base):
    __tablename__ = "tipos_equipo_computo"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(15), unique=True, nullable=False)
    
    # Relaciones
    equipos_computo = relationship("EquipoComputo", back_populates="tipo_equipo")

    # En models/base.py - agregar esta clase
class TipoMobiliario(Base):
    __tablename__ = "tipos_mobiliario"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(25), unique=True, nullable=False)
    
    # Relaciones
    mobiliarios = relationship("Mobiliario", back_populates="tipo_mobiliario")

class TipoPago(Base):
    __tablename__ = "tipos_pago"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(25), unique=True, nullable=False)
    
    # Relación con multas
    multas = relationship("Multa", back_populates="tipo_pago")

class TipoRecursoMulta(Base):
    __tablename__ = "tipos_recurso_multa"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(25), unique=True, nullable=False)
    
    # Relación con multas
    multas = relationship("Multa", back_populates="tipo_recurso_multa")

class TipoUsuario(Base):
    __tablename__ = "tipos_usuario"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(15), unique=True, nullable=False)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="tipo_usuario")