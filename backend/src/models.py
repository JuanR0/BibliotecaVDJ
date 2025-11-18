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

class TipoEquipoComputo(Base):
    __tablename__ = "tipos_equipo_computo"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(15), unique=True, nullable=False)
    
    # Relaciones
    equipos_computo = relationship("EquipoComputo", back_populates="tipo_equipo")

class TipoUsuario(Base):
    __tablename__ = "tipos_usuario"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(15), unique=True, nullable=False)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="tipo_usuario")

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
    edicion = Column(String(50))
    numero_paginas = Column(Integer)
    area_conocimiento_id = Column(Integer, ForeignKey("areas_conocimiento.id"), nullable=False)
    # Información de adquisición
    fecha_adquisicion = Column(TIMESTAMP, server_default=func.now())
    metodo_adquisicion = Column(String(20), nullable=False)
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
    nivel_estudios = Column(String(20), nullable=False)
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