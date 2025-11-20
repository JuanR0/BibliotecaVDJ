-- =============================================
-- TABLAS AUXILIARES (CATÁLOGOS)
-- =============================================

-- Estados para libros
CREATE TABLE estados_libro (
    id SERIAL PRIMARY KEY,
    estado VARCHAR(20) NOT NULL UNIQUE
);

-- Estados para áreas
CREATE TABLE estados_area (
    id SERIAL PRIMARY KEY,
    estado VARCHAR(20) NOT NULL UNIQUE
);

-- Estados para equipos de cómputo
CREATE TABLE estados_equipo (
    id SERIAL PRIMARY KEY,
    estado VARCHAR(20) NOT NULL UNIQUE
);

-- Estados para mobiliario
CREATE TABLE estados_mobiliario (
    id SERIAL PRIMARY KEY,
    estado VARCHAR(20) NOT NULL UNIQUE
);

-- Estados para recursos virtuales
CREATE TABLE estados_virtual (
    id SERIAL PRIMARY KEY,
    estado VARCHAR(20) NOT NULL UNIQUE
);

-- Editoriales de libros
CREATE TABLE editoriales (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Áreas de conocimiento con rangos Dewey
CREATE TABLE areas_conocimiento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    rango_inicio VARCHAR(20) NOT NULL,
    rango_fin VARCHAR(20) NOT NULL
);

-- Relaciones institucionales de usuarios
CREATE TABLE relaciones_institucion (
    id SERIAL PRIMARY KEY,
    relacion VARCHAR(20) NOT NULL UNIQUE
);

-- Marca equipos de computo
CREATE TABLE marcas_equipo_computo(
    id SERIAL PRIMARY KEY,
    marca VARCHAR(100) NOT NULL UNIQUE
);

-- Metodos adquisicion
CREATE TABLE metodos_adquisicion (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(15) NOT NULL UNIQUE
);

-- Niveles estudio
CREATE TABLE niveles_estudio(
    id SERIAL PRIMARY KEY,
    nivel VARCHAR(100) NOT NULL UNIQUE
);

-- Tipos de equipo
CREATE TABLE tipos_equipo_computo (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(15) NOT NULL UNIQUE
);

-- Tipos mobiliario
CREATE TABLE tipos_mobiliario (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(25) NOT NULL UNIQUE
);

-- Tipos de usuario (permisos)
CREATE TABLE tipos_usuario (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(15) NOT NULL UNIQUE
);

-- =============================================
-- TABLAS PRINCIPALES
-- =============================================

-- Usuarios del sistema
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    codigo_universitario VARCHAR(20) NOT NULL UNIQUE,
    clave_acceso VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    relacion_institucional_id INTEGER NOT NULL REFERENCES relaciones_institucion(id),
    tipo_usuario_id INTEGER NOT NULL REFERENCES tipos_usuario(id),
    usuario_creador_id INTEGER REFERENCES usuarios(id),  
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    esta_activo BOOLEAN DEFAULT TRUE,
    fecha_ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Áreas físicas de la biblioteca
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    capacidad INTEGER,
    es_prestable BOOLEAN NOT NULL DEFAULT FALSE,
    usuario_registro_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    estado_id INTEGER NOT NULL REFERENCES estados_area(id),
    fecha_ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Libros físicos
CREATE TABLE libros (
    id SERIAL PRIMARY KEY,
    -- Identificación física
    codigo_decimal VARCHAR(20) NOT NULL,
    etiqueta CHAR(3) NOT NULL,
    numero_ejemplar INTEGER NOT NULL,
    -- Metadatos del libro
    isbn VARCHAR(20),
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    editorial_id INTEGER NOT NULL REFERENCES editoriales(id),
    edicion INTEGER, 
    numero_paginas INTEGER,
    area_conocimiento_id INTEGER NOT NULL REFERENCES areas_conocimiento(id),
    -- Información de adquisición
    fecha_adquisicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo_adquisicion_id INTEGER NOT NULL REFERENCES metodos_adquisicion(id),  
    proveedor_nombre VARCHAR(255),
    precio DECIMAL(10,2),
    es_prestable BOOLEAN NOT NULL DEFAULT TRUE,
    -- Seguimiento y estado
    usuario_registro_id INTEGER NOT NULL REFERENCES usuarios(id),
    estado_id INTEGER NOT NULL REFERENCES estados_libro(id),
    fecha_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints de unicidad
    UNIQUE(codigo_decimal, etiqueta, numero_ejemplar)
);

-- Equipos de cómputo
CREATE TABLE equipos_computo (
    id SERIAL PRIMARY KEY,
    numero_serie VARCHAR(50) NOT NULL UNIQUE,
    marca_id INTEGER NOT NULL REFERENCES marcas_equipo_computo,
    modelo VARCHAR(50) NOT NULL,
    tipo_equipo_id INTEGER NOT NULL REFERENCES tipos_equipo_computo(id),
    especificaciones TEXT,
    es_prestable BOOLEAN NOT NULL DEFAULT TRUE,
    usuario_registro_id INTEGER NOT NULL REFERENCES usuarios(id),  
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    area_id INTEGER NOT NULL REFERENCES areas(id),
    estado_id INTEGER NOT NULL REFERENCES estados_equipo(id),
    fecha_ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mobiliario 
CREATE TABLE mobiliario (
    id SERIAL PRIMARY KEY,
    tipo_mobiliario_id INTEGER NOT NULL REFERENCES tipos_mobiliario(id),  
    descripcion VARCHAR(255),
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creador_id INTEGER NOT NULL REFERENCES usuarios(id),  
    area_id INTEGER NOT NULL REFERENCES areas(id),
    estado_id INTEGER NOT NULL REFERENCES estados_mobiliario(id),
    fecha_ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Libros virtuales/digitales
CREATE TABLE libros_virtuales (
    id SERIAL PRIMARY KEY,
    -- Metadatos del libro
    isbn VARCHAR(20),
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    editorial_id INTEGER NOT NULL REFERENCES editoriales(id),
    edicion INTEGER,
    numero_paginas INTEGER,
    area_conocimiento_id INTEGER NOT NULL REFERENCES areas_conocimiento(id),
    -- Relevante a lo digital
    archivo_digital VARCHAR(255) NOT NULL,
    usuario_subio_id INTEGER NOT NULL REFERENCES usuarios(id),    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_virtual_id INTEGER NOT NULL REFERENCES estados_virtual(id),
    fecha_ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tesis
CREATE TABLE tesis (
    id SERIAL PRIMARY KEY,
    codigo_decimal VARCHAR(20) NOT NULL UNIQUE,
    titulo VARCHAR(500) NOT NULL,
    numero_paginas INTEGER,
    fecha_publicacion VARCHAR(50) NOT NULL,
    -- Información del autor
    nombre_autor VARCHAR(255) NOT NULL,
    codigo_universitario_autor VARCHAR(20) NOT NULL,
    generacion VARCHAR(10),
    carrera VARCHAR(100) NOT NULL,
    nivel_estudios_id INTEGER NOT NULL REFERENCES niveles_estudio(id),
    -- Fisico
    usuario_ingreso_id INTEGER NOT NULL REFERENCES usuarios(id),  
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_fisico_id INTEGER NOT NULL REFERENCES estados_libro(id),
    fecha_ultimo_cambio_estado_fisico TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Virtual
    usuario_subio_virtual_id INTEGER REFERENCES usuarios(id),
    fecha_subida_virtual TIMESTAMP,
    link_copia_virtual VARCHAR(255),     
    estado_virtual_id INTEGER NOT NULL REFERENCES estados_virtual(id),
    fecha_ultimo_cambio_estado_virtual TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- ÍNDICES PARA MEJOR PERFORMANCE
-- =============================================

-- Índices para búsquedas frecuentes
-- CREATE INDEX idx_libros_titulo ON libros(titulo);
-- CREATE INDEX idx_libros_autor ON libros(autor);
-- CREATE INDEX idx_usuarios_codigo ON usuarios(codigo_universitario);
-- CREATE INDEX idx_tesis_autor ON tesis(nombre_autor);
-- CREATE INDEX idx_tesis_carrera ON tesis(carrera);