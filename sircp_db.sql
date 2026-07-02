-- =============================================
-- S.I.R.C.P.  — Script de Base de Datos
-- =============================================

-- Crear la base de datos si no existe
DROP DATABASE IF EXISTS sircp_db;
CREATE DATABASE IF NOT EXISTS sircp_db;
USE sircp_db;

-- =============================================
-- TABLA: plataformas
-- Tiendas disponibles para rastreo
-- =============================================
CREATE TABLE IF NOT EXISTS plataformas (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Datos iniciales de plataformas
INSERT IGNORE INTO plataformas (nombre) VALUES
    ('Fravega'),
    ('OnCity'),
    ('Naldo'),
    ('FGStore'),
    ('Megatone'),
    ('MercadoLibre');

-- =============================================
-- TABLA: productos
-- Productos buscados por los usuarios
-- =============================================
CREATE TABLE IF NOT EXISTS productos (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nombre    VARCHAR(255) NOT NULL,
    categoria VARCHAR(50)  DEFAULT 'Tecnología'
);

-- =============================================
-- TABLA: historial_precios
-- Registro histórico de precios mínimos detectados
-- =============================================
CREATE TABLE IF NOT EXISTS historial_precios (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    producto_id   INT            NOT NULL,
    plataforma_id INT            NOT NULL,
    precio        DECIMAL(12, 2) NOT NULL,
    fecha         DATETIME       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id)   REFERENCES productos(id)   ON DELETE CASCADE,
    FOREIGN KEY (plataforma_id) REFERENCES plataformas(id) ON DELETE CASCADE
);

-- =============================================
-- TABLA: usuarios 
-- Cuentas de usuarios registrados
-- =============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100)        NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    password_hash   VARCHAR(64)         NOT NULL,
    fecha_registro  DATETIME            DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- TABLA: favoritos 
-- Productos guardados por cada usuario con umbral de alerta
-- =============================================
CREATE TABLE IF NOT EXISTS favoritos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id      INT            NOT NULL,
    producto_id     INT            NOT NULL,
    umbral_precio   DECIMAL(12, 2) DEFAULT NULL,
    alerta_activa   TINYINT(1)     DEFAULT 0,
    fecha_agregado  DATETIME       DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_usuario_producto (usuario_id, producto_id),
    FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)  ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

-- =============================================
-- VERIFICACIÓN FINAL
-- Muestra las tablas creadas
-- =============================================
SHOW TABLES;
