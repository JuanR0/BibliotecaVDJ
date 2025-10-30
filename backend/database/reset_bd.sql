-- Script para reiniciar completamente la base de datos
DROP DATABASE IF EXISTS bibliotecavdj;
CREATE DATABASE bibliotecavdj;

\c bibliotecavdj

-- Ejecutar esquema completo
\i 01_esquema_completo.sql

-- Ejecutar datos de referencia
\i 02_datos_referencia.sql