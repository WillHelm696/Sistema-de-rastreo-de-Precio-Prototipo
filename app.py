from flask import Flask, jsonify, render_template, request, session
from db_manager import obtener_conexion
import hashlib
import os

# --- Importar funciones de scraping ---
from scraper_tools import (
    scrap_fgstore,
    scrap_naldo,
    scrap_fravega,
    scrap_oncity,
    scrap_megatone
)

app = Flask(__name__)
# Clave secreta para manejar sesiones de Flask
app.secret_key = os.environ.get('SECRET_KEY', 'sircp_clave_secreta_2026')


# =============================================
# 1. FUNCIONES AUXILIARES - GENERALES
# =============================================

def validar_datos_entrada(data):
    """
    Valida que los datos recibidos en la petición sean correctos.
    """
    if not data:
        return False, "No se recibieron datos válidos"
    producto_buscado = data.get('producto', '').strip()
    if not producto_buscado:
        return False, "El nombre del producto está vacío"
    plataformas_solicitadas = data.get('plataformas', [])
    if not plataformas_solicitadas:
        return False, "No se seleccionó ninguna plataforma"
    return True, ""

def hashear_password(password):
    """Genera un hash SHA-256 de la contraseña recibida."""
    return hashlib.sha256(password.encode()).hexdigest()

def obtener_usuario_sesion():
    """Devuelve el ID del usuario en sesión, o None si no hay sesión activa."""
    return session.get('usuario_id')

def obtener_o_crear_producto(cursor, conexion, producto_buscado, categoria='Tecnología'):
    """
    Busca un producto en la base de datos. Si no existe, lo crea.
    """
    cursor.execute(
        "SELECT id, categoria FROM productos WHERE nombre = %s",
        (producto_buscado,)
    )
    producto_local = cursor.fetchone()
    if producto_local:
        return producto_local['id'], producto_local['categoria']
    else:
        cursor.execute(
            "INSERT INTO productos (nombre, categoria) VALUES (%s, %s)",
            (producto_buscado, categoria)
        )
        conexion.commit()
        return cursor.lastrowid, categoria

def obtener_plataformas_db(cursor):
    """
    Obtiene todas las plataformas de la base de datos como diccionario.
    """
    cursor.execute("SELECT id, nombre FROM plataformas")
    return {row['nombre']: row['id'] for row in cursor.fetchall()}

def ejecutar_scraping(producto_buscado, plataformas_solicitadas, plataformas_db):
    """
    Ejecuta el scraping para cada plataforma solicitada.
    """
    desglose_resultados = []
    mapeo_scrapers = {
        "Fravega": scrap_fravega,
        "OnCity":  scrap_oncity,
        "Naldo":   scrap_naldo,
        "FGStore": scrap_fgstore,
        "Megatone": scrap_megatone
    }

    for nombre_tienda in plataformas_solicitadas:
        if nombre_tienda not in plataformas_db:
            continue
        plat_id = plataformas_db[nombre_tienda]
        scraper_func = mapeo_scrapers.get(nombre_tienda)

        if scraper_func:
            resultados_scraping = scraper_func(producto_buscado)
            if resultados_scraping:
                for resultado in resultados_scraping:
                    precio_str = (
                        resultado.get('precio') or
                        resultado.get('precio_venta') or
                        resultado.get('precio_promocional')
                    )
                    url_compra     = resultado.get('url', '#')
                    nombre_producto = resultado.get('nombre_producto', producto_buscado)

                    precio_final = None
                    if precio_str is not None and precio_str != "No disponible":
                        try:
                            precio_final = float(
                                str(precio_str)
                                .replace('$', '')
                                .replace('.', '')
                                .replace(',', '.')
                            )
                        except (ValueError, TypeError, AttributeError):
                            precio_final = None

                    desglose_resultados.append({
                        "plataforma_id": plat_id,
                        "tienda":         nombre_tienda,
                        "precio":         precio_final,
                        "url_compra":     url_compra,
                        "nombre_producto": nombre_producto
                    })
            else:
                desglose_resultados.append({
                    "plataforma_id": plat_id,
                    "tienda":         nombre_tienda,
                    "precio":         None,
                    "url_compra":     "#",
                    "nombre_producto": producto_buscado
                })
        else:
            desglose_resultados.append({
                "plataforma_id": plat_id,
                "tienda":         nombre_tienda,
                "precio":         None,
                "url_compra":     "#",
                "nombre_producto": producto_buscado
            })

    return desglose_resultados

def registrar_historial_y_obtener_minimo(conexion, producto_id, desglose_resultados):
    """
    Registra el precio mínimo en el historial y devuelve historial + mínimo absoluto.
    """
    cursor = conexion.cursor(dictionary=True)
    ofertas_validas = [o for o in desglose_resultados if o['precio'] and o['precio'] > 0]

    if ofertas_validas:
        oferta_minima = min(ofertas_validas, key=lambda x: x['precio'])
        cursor.execute(
            "INSERT INTO historial_precios (producto_id, plataforma_id, precio) VALUES (%s, %s, %s)",
            (producto_id, oferta_minima['plataforma_id'], oferta_minima['precio'])
        )
        conexion.commit()

    cursor.execute("""
        SELECT h.precio, h.fecha, p.nombre AS tienda
        FROM historial_precios h
        INNER JOIN plataformas p ON h.plataforma_id = p.id
        WHERE h.producto_id = %s
        ORDER BY h.fecha DESC
    """, (producto_id,))
    historial_completo = cursor.fetchall()

    for registro in historial_completo:
        registro['fecha'] = registro['fecha'].strftime('%d/%m/%Y %H:%M:%S')

    cursor.execute(
        "SELECT MIN(precio) AS minimo_absoluto FROM historial_precios WHERE producto_id = %s",
        (producto_id,)
    )
    row = cursor.fetchone()
    minimo_absoluto = row['minimo_absoluto'] if row else None

    cursor.close()
    return historial_completo, minimo_absoluto


# =============================================
# 2. RUTAS - AUTENTICACIÓN
# =============================================

@app.route('/')
def index():
    """Ruta principal: sirve el template index.html."""
    return render_template('index.html')

@app.route('/api/registro', methods=['POST'])
def registro():
    """
    Registra un nuevo usuario.
    Recibe: { "nombre": str, "email": str, "password": str }
    """
    try:
        data = request.get_json()
        nombre   = data.get('nombre', '').strip()
        email    = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not nombre or not email or not password:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400
        if len(password) < 6:
            return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

        conexion = obtener_conexion()
        cursor   = conexion.cursor(dictionary=True)

        # Verificar si el email ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return jsonify({"error": "El email ya está registrado"}), 409

        password_hash = hashear_password(password)
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)",
            (nombre, email, password_hash)
        )
        conexion.commit()
        usuario_id = cursor.lastrowid
        cursor.close()
        conexion.close()

        # Iniciar sesión automáticamente tras el registro
        session['usuario_id'] = usuario_id
        session['usuario_nombre'] = nombre

        return jsonify({"ok": True, "nombre": nombre})

    except Exception as e:
        print(f"[-] Error en registro: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """
    Inicia sesión de un usuario existente.
    Recibe: { "email": str, "password": str }
    """
    try:
        data     = request.get_json()
        email    = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"error": "Email y contraseña son obligatorios"}), 400

        conexion = obtener_conexion()
        cursor   = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, password_hash FROM usuarios WHERE email = %s",
            (email,)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not usuario or usuario['password_hash'] != hashear_password(password):
            return jsonify({"error": "Credenciales incorrectas"}), 401

        session['usuario_id']     = usuario['id']
        session['usuario_nombre'] = usuario['nombre']

        return jsonify({"ok": True, "nombre": usuario['nombre']})

    except Exception as e:
        print(f"[-] Error en login: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    return jsonify({"ok": True})

@app.route('/api/sesion', methods=['GET'])
def verificar_sesion():
    """Verifica si hay una sesión activa y devuelve los datos del usuario."""
    usuario_id = obtener_usuario_sesion()
    if usuario_id:
        return jsonify({
            "autenticado": True,
            "nombre": session.get('usuario_nombre')
        })
    return jsonify({"autenticado": False})


# =============================================
# 3. RUTA PRINCIPAL - RASTREO DE PRECIOS
# =============================================

@app.route('/api/rastrear', methods=['POST'])
def rastrear_producto():
    """
    Endpoint para rastrear precios. Requiere sesión activa.
    Recibe: { "producto": str, "plataformas": [str], "categoria": str }
    """
    try:
        # Verificar autenticación
        if not obtener_usuario_sesion():
            return jsonify({"error": "No autenticado"}), 401

        data = request.get_json()
        es_valido, mensaje_error = validar_datos_entrada(data)
        if not es_valido:
            return jsonify({"error": mensaje_error}), 400

        producto_buscado      = data.get('producto', '').strip()
        plataformas_solicitadas = data.get('plataformas', [])
        categoria             = data.get('categoria', 'Tecnología')

        conexion = obtener_conexion()
        cursor   = conexion.cursor(dictionary=True)

        producto_id, categoria = obtener_o_crear_producto(
            cursor, conexion, producto_buscado, categoria
        )
        plataformas_db  = obtener_plataformas_db(cursor)
        cursor.close()

        desglose_resultados = ejecutar_scraping(
            producto_buscado, plataformas_solicitadas, plataformas_db
        )
        historial_completo, minimo_absoluto = registrar_historial_y_obtener_minimo(
            conexion, producto_id, desglose_resultados
        )
        conexion.close()

        ofertas_validas = [o for o in desglose_resultados if o['precio'] and o['precio'] > 0]
        oferta_minima   = min(ofertas_validas, key=lambda x: x['precio']) if ofertas_validas else None

        respuesta = {
            "producto":               producto_buscado,
            "categoria":              categoria,
            "producto_id":            producto_id,
            "costo_minimo_detectado": oferta_minima['precio'] if oferta_minima else 0,
            "tienda_mas_barata":      oferta_minima['tienda'] if oferta_minima else "-",
            "historial_minimo_absoluto": minimo_absoluto,
            "desglose":               desglose_resultados,
            "historial_completo":     historial_completo
        }
        return jsonify(respuesta)

    except Exception as e:
        print(f"[-] Error en backend: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================
# 4. RUTAS - FAVORITOS
# =============================================

@app.route('/api/favoritos', methods=['GET'])
def obtener_favoritos():
    """Devuelve los productos favoritos del usuario en sesión."""
    usuario_id = obtener_usuario_sesion()
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    try:
        conexion = obtener_conexion()
        cursor   = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id, f.producto_id, f.umbral_precio, f.alerta_activa,
                   p.nombre AS nombre_producto, p.categoria,
                   (SELECT MIN(h.precio)
                    FROM historial_precios h
                    WHERE h.producto_id = f.producto_id) AS precio_minimo_historico,
                   (SELECT h2.precio
                    FROM historial_precios h2
                    WHERE h2.producto_id = f.producto_id
                    ORDER BY h2.fecha DESC LIMIT 1) AS precio_actual
            FROM favoritos f
            INNER JOIN productos p ON f.producto_id = p.id
            WHERE f.usuario_id = %s
            ORDER BY f.fecha_agregado DESC
        """, (usuario_id,))
        favoritos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify({"favoritos": favoritos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favoritos', methods=['POST'])
def agregar_favorito():
    """
    Agrega un producto a favoritos del usuario en sesión.
    Recibe: { "producto_id": int, "umbral_precio": float (opcional) }
    """
    usuario_id = obtener_usuario_sesion()
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data        = request.get_json()
        producto_id  = data.get('producto_id')
        umbral      = data.get('umbral_precio')

        if not producto_id:
            return jsonify({"error": "producto_id es requerido"}), 400

        conexion = obtener_conexion()
        cursor   = conexion.cursor(dictionary=True)

        # Evitar duplicados
        cursor.execute(
            "SELECT id FROM favoritos WHERE usuario_id = %s AND producto_id = %s",
            (usuario_id, producto_id)
        )
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return jsonify({"error": "El producto ya está en favoritos"}), 409

        cursor.execute(
            "INSERT INTO favoritos (usuario_id, producto_id, umbral_precio) VALUES (%s, %s, %s)",
            (usuario_id, producto_id, umbral)
        )
        conexion.commit()
        favorito_id = cursor.lastrowid
        cursor.close()
        conexion.close()

        return jsonify({"ok": True, "favorito_id": favorito_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favoritos/<int:favorito_id>', methods=['DELETE'])
def eliminar_favorito(favorito_id):
    """Elimina un favorito del usuario en sesión."""
    usuario_id = obtener_usuario_sesion()
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    try:
        conexion = obtener_conexion()
        cursor   = conexion.cursor()
        cursor.execute(
            "DELETE FROM favoritos WHERE id = %s AND usuario_id = %s",
            (favorito_id, usuario_id)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favoritos/<int:favorito_id>/umbral', methods=['PUT'])
def actualizar_umbral(favorito_id):
    """
    Actualiza el umbral de precio de un favorito.
    Recibe: { "umbral_precio": float }
    """
    usuario_id = obtener_usuario_sesion()
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data   = request.get_json()
        umbral = data.get('umbral_precio')

        conexion = obtener_conexion()
        cursor   = conexion.cursor()
        cursor.execute(
            "UPDATE favoritos SET umbral_precio = %s, alerta_activa = 1 WHERE id = %s AND usuario_id = %s",
            (umbral, favorito_id, usuario_id)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================
# 5. RUTAS - ALERTAS
# =============================================

@app.route('/api/alertas/verificar', methods=['GET'])
def verificar_alertas():
    """
    Verifica las alertas del usuario: devuelve favoritos cuyo precio actual
    es menor o igual al umbral definido.
    """
    usuario_id = obtener_usuario_sesion()
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    try:
        conexion = obtener_conexion()
        cursor   = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id, f.umbral_precio, p.nombre AS nombre_producto,
                   (SELECT h.precio
                    FROM historial_precios h
                    WHERE h.producto_id = f.producto_id
                    ORDER BY h.fecha DESC LIMIT 1) AS precio_actual
            FROM favoritos f
            INNER JOIN productos p ON f.producto_id = p.id
            WHERE f.usuario_id = %s AND f.alerta_activa = 1 AND f.umbral_precio IS NOT NULL
        """, (usuario_id,))
        alertas_pendientes = []
        for row in cursor.fetchall():
            if row['precio_actual'] and row['umbral_precio']:
                if row['precio_actual'] <= row['umbral_precio']:
                    alertas_pendientes.append({
                        "favorito_id":      row['id'],
                        "nombre_producto":  row['nombre_producto'],
                        "precio_actual":    row['precio_actual'],
                        "umbral_precio":    row['umbral_precio']
                    })
        cursor.close()
        conexion.close()
        return jsonify({"alertas": alertas_pendientes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================
# 6. EJECUCIÓN DEL SERVIDOR
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
