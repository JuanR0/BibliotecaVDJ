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
    relacion_id INTEGER NOT NULL REFERENCES relaciones_institucion(id),
    tipo_usuario_id INTEGER NOT NULL REFERENCES tipos_usuario(id),
    usuario_creador_id INTEGER REFERENCES usuarios(id),  -- Quién dio de alta al usuario
    ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    esta_activo BOOLEAN DEFAULT TRUE
);

-- Áreas físicas de la biblioteca
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    capacidad INTEGER,
    es_prestable BOOLEAN NOT NULL DEFAULT FALSE,
    usuario_creador_id INTEGER NOT NULL REFERENCES usuarios(id),  -- Quién creó el área
    estado_id INTEGER NOT NULL REFERENCES estados_area(id),
    ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    edicion VARCHAR(50),
    numero_paginas INTEGER,
    area_id INTEGER NOT NULL REFERENCES areas_conocimiento(id),
    -- Información de adquisición
    fecha_adquisicion DATE DEFAULT CURRENT_DATE,
    metodo_adquisicion VARCHAR(20) NOT NULL,
    proveedor_nombre VARCHAR(255),
    precio DECIMAL(10,2),
    -- Seguimiento y estado
    usuario_creador_id INTEGER NOT NULL REFERENCES usuarios(id),  -- Quién registró el libro
    estado_id INTEGER NOT NULL REFERENCES estados_libro(id),
    fecha_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    es_prestable BOOLEAN NOT NULL DEFAULT TRUE,
    -- Constraints de unicidad
    UNIQUE(codigo_decimal, etiqueta, numero_ejemplar)
);

-- Equipos de cómputo
CREATE TABLE equipos_computo (
    id SERIAL PRIMARY KEY,
    numero_serie VARCHAR(50) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    tipo_equipo VARCHAR(20) NOT NULL,
    especificaciones TEXT,
    fecha_adquisicion DATE DEFAULT CURRENT_DATE,
    destino_uso VARCHAR(30) NOT NULL,
    usuario_creador_id INTEGER NOT NULL REFERENCES usuarios(id),  -- Quién registró el equipo
    area_id INTEGER NOT NULL REFERENCES areas(id),
    estado_id INTEGER NOT NULL REFERENCES estados_equipo(id),
    ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mobiliario
CREATE TABLE mobiliario (
    id SERIAL PRIMARY KEY,
    tipo_mobiliario VARCHAR(30) NOT NULL,
    descripcion VARCHAR(255),
    fecha_ingreso DATE DEFAULT CURRENT_DATE,
    usuario_creador_id INTEGER NOT NULL REFERENCES usuarios(id),  -- Quién registró el mobiliario
    area_id INTEGER NOT NULL REFERENCES areas(id),
    estado_id INTEGER NOT NULL REFERENCES estados_mobiliario(id),
    ultimo_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Libros virtuales/digitales
CREATE TABLE libros_virtuales (
    id SERIAL PRIMARY KEY,
    archivo_digital VARCHAR(255) NOT NULL,
    formato VARCHAR(10),
    tamanio_bytes BIGINT,
    usuario_subio_id INTEGER NOT NULL REFERENCES usuarios(id),    -- Quién subió el archivo
    estado_virtual_id INTEGER NOT NULL REFERENCES estados_virtual(id),
    fecha_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tesis
CREATE TABLE tesis (
    id SERIAL PRIMARY KEY,
    codigo_decimal VARCHAR(20) NOT NULL UNIQUE,
    titulo VARCHAR(500) NOT NULL,
    numero_paginas INTEGER,
    fecha_publicacion DATE NOT NULL,
    -- Información del autor
    nombre_autor VARCHAR(255) NOT NULL,
    codigo_universitario VARCHAR(20) NOT NULL,
    generacion VARCHAR(10),
    carrera VARCHAR(100) NOT NULL,
    nivel_estudios VARCHAR(20) NOT NULL,
    -- Tracking de subida
    usuario_subio_id INTEGER NOT NULL REFERENCES usuarios(id),    -- Quién registró la tesis
    link_copia_virtual VARCHAR(255),
    fecha_subida_virtual TIMESTAMP,
    usuario_subio_virtual_id INTEGER REFERENCES usuarios(id),     -- Quién subió la copia virtual
    estado_virtual_id INTEGER REFERENCES estados_virtual(id),
    fecha_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Seguimiento
    estado VARCHAR(20) DEFAULT 'Disponible',
    fecha_ingreso DATE DEFAULT CURRENT_DATE
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