import mysql.connector

# =============================================
# CONEXIÓN A LA BASE DE DATOS
# =============================================

def obtener_conexion():
    """
    Devuelve una conexión activa a la base de datos MySQL.
    Ajustar host, user, password y database según el entorno.
    """
    return mysql.connector.connect(
        host="localhost",
        user="Tu_Usuario",
        password="Tu_Contraseña",
        database="sircp_db"
    )


# =============================================
# FUNCIONES DE HISTORIAL (compatibilidad original)
# =============================================

def registrar_precio_historial(producto_id, plataforma_id, precio):
    """Inserta un registro de precio en el historial."""
    conexion = obtener_conexion()
    cursor   = conexion.cursor()
    cursor.execute(
        "INSERT INTO historial_precios (producto_id, plataforma_id, precio) VALUES (%s, %s, %s)",
        (producto_id, plataforma_id, precio)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def obtener_minimo_absoluto(producto_id):
    """Obtiene el precio mínimo histórico de un producto."""
    conexion = obtener_conexion()
    cursor   = conexion.cursor()
    cursor.execute(
        "SELECT MIN(precio) FROM historial_precios WHERE producto_id = %s",
        (producto_id,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado[0] if resultado else None


# =============================================
# SCRIPT SQL PARA CREAR/ACTUALIZAR TABLAS
# Ejecutar en MySQL Workbench o consola MySQL
# =============================================
#
# -- Tabla de usuarios (NUEVA)
# CREATE TABLE IF NOT EXISTS usuarios (
#     id            INT AUTO_INCREMENT PRIMARY KEY,
#     nombre        VARCHAR(100)        NOT NULL,
#     email         VARCHAR(150) UNIQUE NOT NULL,
#     password_hash VARCHAR(64)         NOT NULL,
#     fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
# );
#
# -- Tabla de productos (ya existente, sin cambios)
# CREATE TABLE IF NOT EXISTS productos (
#     id        INT AUTO_INCREMENT PRIMARY KEY,
#     nombre    VARCHAR(255) NOT NULL,
#     categoria VARCHAR(50)  DEFAULT 'Tecnología'
# );
#
# -- Tabla de plataformas (ya existente, sin cambios)
# CREATE TABLE IF NOT EXISTS plataformas (
#     id     INT AUTO_INCREMENT PRIMARY KEY,
#     nombre VARCHAR(100) NOT NULL
# );
#
# -- Tabla de historial de precios (ya existente, sin cambios)
# CREATE TABLE IF NOT EXISTS historial_precios (
#     id            INT AUTO_INCREMENT PRIMARY KEY,
#     producto_id   INT            NOT NULL,
#     plataforma_id INT            NOT NULL,
#     precio        DECIMAL(12, 2) NOT NULL,
#     fecha         DATETIME DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (producto_id)   REFERENCES productos(id),
#     FOREIGN KEY (plataforma_id) REFERENCES plataformas(id)
# );
#
# -- Tabla de favoritos (NUEVA)
# CREATE TABLE IF NOT EXISTS favoritos (
#     id              INT AUTO_INCREMENT PRIMARY KEY,
#     usuario_id      INT            NOT NULL,
#     producto_id     INT            NOT NULL,
#     umbral_precio   DECIMAL(12, 2) DEFAULT NULL,
#     alerta_activa   TINYINT(1)     DEFAULT 0,
#     fecha_agregado  DATETIME       DEFAULT CURRENT_TIMESTAMP,
#     UNIQUE KEY uq_usuario_producto (usuario_id, producto_id),
#     FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)  ON DELETE CASCADE,
#     FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
# );
#
# -- Datos iniciales de plataformas (si la tabla está vacía)
# INSERT IGNORE INTO plataformas (nombre) VALUES
#     ('Fravega'), ('OnCity'), ('Naldo'), ('FGStore'), ('Megatone');
