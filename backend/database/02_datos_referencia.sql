-- Estados para libros
INSERT INTO estados_libro (estado) VALUES 
('Disponible'),
('Prestado'), 
('Mantenimiento'),
('Retirado');

-- Estados para áreas
INSERT INTO estados_area (estado) VALUES 
('Disponible'),
('Ocupada'),
('Mantenimiento'), 
('Reservada'),
('No disponible');

-- Estados para equipos
INSERT INTO estados_equipo (estado) VALUES 
('Disponible'),
('Prestado'),
('Mantenimiento'),
('Asignado'),
('Retirado');

-- Estados para mobiliario
INSERT INTO estados_mobiliario (estado) VALUES 
('En uso'),
('En reparación'),
('Almacenado'),
('Dado de baja');

-- Estados para multa
INSERT INTO estados_multa (estado) VALUES 
('Pendiente'),
('Liquidada');

-- Insertar estados básicos de préstamo
INSERT INTO estados_prestamo (estado) VALUES 
('Vigente'),
('Expirado'),
('Terminado'),
('Otros');

-- Estados para recursos virtuales
INSERT INTO estados_virtual (estado) VALUES 
('Disponible'),
('No disponible');

-- Editoriales
INSERT INTO editoriales (nombre) VALUES 
('Penguin Random House'),
('McGraw-Hill'),
('Oxford University Press');

-- Áreas de conocimiento
INSERT INTO areas_conocimiento (nombre, rango_inicio, rango_fin) VALUES 
('Matemáticas', '510', '519'),
('Química', '540', '549'),
('Física', '530', '539'),
('Literatura', '860', '869'),
('Otros', '000', '999');

-- Relaciones institucionales
INSERT INTO relaciones_institucion (relacion) VALUES 
('Estudiante'),
('Academico'),
('Administrativo'), 
('Otro');

-- Marcas equipo computo
INSERT INTO marcas_equipo_computo (marca) VALUES 
('HP'),
('LENOVO'),
('DELL');

-- Metodos de adquisicion
INSERT INTO metodos_adquisicion (tipo) VALUES 
('Compra'),
('Donacion');

-- Tipos de niveles de estudio
INSERT INTO niveles_estudio (nivel) VALUES 
('Licenciatura'),
('Maestria'),
('Doctorado');

-- Tipos de equipo computo
INSERT INTO tipos_equipo_computo (tipo) VALUES 
('Portatil'),
('De escritorio');

-- Tipos de mobiliario
INSERT INTO tipos_mobiliario (tipo) VALUES 
('Silla'),
('Mesa'),
('Escritorio'),
('Sillon');

-- Tipos de pago
INSERT INTO tipos_pago (tipo) VALUES 
('Monetario'),
('En especie'),
('Ambos');

-- Tipos de recurso para multa
INSERT INTO tipos_recurso_multa (tipo) VALUES 
('Libro'),
('Equipo_computo'),
('Mobiliario'),
('Infraestructura'),
('Otro');

-- Tipos de usuario
INSERT INTO tipos_usuario (tipo) VALUES 
('Comun'),
('Admin_basico'),
('Admin_avanzado'),
('SuperAdmin');