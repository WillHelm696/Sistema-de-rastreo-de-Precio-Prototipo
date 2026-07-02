/**
 * S.I.R.C.P.  — Lógica de Frontend
 * Módulos: Autenticación, Búsqueda por Categorías,
 *           Favoritos y Sistema de Alertas.
 */

// =============================================
// ESTADO GLOBAL DE LA APLICACIÓN
// =============================================

/** Almacena el último resultado de búsqueda para usarlo en favoritos. */
let ultimaBusqueda = {
    producto_id:  null,
    producto:     null,
    categoria:    null
};

/** Categoría actualmente seleccionada en la interfaz. */
let categoriaActual = 'Tecnología';


// =============================================
// 1. UTILIDADES GENERALES
// =============================================

/**
 * Formatea un número como precio en pesos argentinos.
 * @param {number} valor
 * @returns {string}
 */
function formatearPrecio(valor) {
    if (!valor && valor !== 0) return '-';
    return '$' + Number(valor).toLocaleString('es-AR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Muestra un toast de notificación temporal en pantalla.
 * @param {string} mensaje - Texto a mostrar.
 * @param {'ok'|'error'|'info'} tipo - Estilo visual.
 * @param {number} duracion - Milisegundos que permanece visible (default 3000).
 */
function mostrarToast(mensaje, tipo = 'info', duracion = 3000) {
    const toast = document.getElementById('toast');
    toast.textContent   = mensaje;
    toast.className     = `toast toast-${tipo}`;
    toast.style.display = 'block';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
        toast.style.display = 'none';
    }, duracion);
}

/**
 * Cambia la sección visible de la aplicación y marca la píldora activa.
 * @param {string} nombre - 'busqueda' | 'favoritos' | 'alertas'
 */
function mostrarSeccion(nombre) {
    const secciones = ['busqueda', 'favoritos', 'alertas'];
    secciones.forEach(s => {
        document.getElementById(`seccion-${s}`).style.display =
            (s === nombre) ? 'block' : 'none';
    });

    document.querySelectorAll('.nav-pill').forEach((pill, i) => {
        pill.classList.toggle('active', secciones[i] === nombre);
    });

    // Cargar datos al entrar en favoritos o alertas
    if (nombre === 'favoritos') cargarFavoritos();
    if (nombre === 'alertas')   verificarAlertas();
}


// =============================================
// 2. AUTENTICACIÓN
// =============================================

/**
 * Cambia entre los formularios de Login y Registro.
 * @param {string} tab - 'login' | 'registro'
 */
function cambiarTab(tab) {
    document.getElementById('form-login').style.display   = tab === 'login'    ? 'block' : 'none';
    document.getElementById('form-registro').style.display = tab === 'registro' ? 'block' : 'none';
    document.querySelectorAll('.auth-tab').forEach((btn, i) => {
        btn.classList.toggle('active', (i === 0 && tab === 'login') || (i === 1 && tab === 'registro'));
    });
    // Limpiar mensajes de error al cambiar pestaña
    ocultarError('login-error');
    ocultarError('reg-error');
}

function mostrarError(id, texto) {
    const el = document.getElementById(id);
    el.textContent    = texto;
    el.style.display  = 'block';
}

function ocultarError(id) {
    document.getElementById(id).style.display = 'none';
}

/** Verifica si hay sesión activa al cargar la página. */
async function verificarSesionInicial() {
    try {
        const resp = await fetch('/api/sesion');
        const data = await resp.json();
        if (data.autenticado) {
            activarApp(data.nombre);
        }
    } catch (e) {
        console.warn('No se pudo verificar la sesión:', e);
    }
}

/**
 * Muestra la pantalla principal y oculta la de autenticación.
 * @param {string} nombre - Nombre del usuario autenticado.
 */
function activarApp(nombre) {
    document.getElementById('pantalla-auth').style.display   = 'none';
    document.getElementById('app-principal').style.display   = 'block';
    document.getElementById('nombre-usuario').textContent    = nombre;
}

/** Ejecuta el inicio de sesión con los datos del formulario. */
async function ejecutarLogin() {
    ocultarError('login-error');
    const email    = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();

    if (!email || !password) {
        mostrarError('login-error', 'Completá todos los campos.');
        return;
    }

    try {
        const resp = await fetch('/api/login', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ email, password })
        });
        const data = await resp.json();
        if (data.error) {
            mostrarError('login-error', data.error);
        } else {
            activarApp(data.nombre);
            mostrarToast(`¡Bienvenido/a, ${data.nombre}! 👋`, 'ok');
        }
    } catch (e) {
        mostrarError('login-error', 'Error de conexión con el servidor.');
    }
}

/** Ejecuta el registro con los datos del formulario. */
async function ejecutarRegistro() {
    ocultarError('reg-error');
    const nombre   = document.getElementById('reg-nombre').value.trim();
    const email    = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value.trim();

    if (!nombre || !email || !password) {
        mostrarError('reg-error', 'Completá todos los campos.');
        return;
    }
    if (password.length < 6) {
        mostrarError('reg-error', 'La contraseña debe tener al menos 6 caracteres.');
        return;
    }

    try {
        const resp = await fetch('/api/registro', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ nombre, email, password })
        });
        const data = await resp.json();
        if (data.error) {
            mostrarError('reg-error', data.error);
        } else {
            activarApp(data.nombre);
            mostrarToast(`¡Cuenta creada exitosamente! Bienvenido/a, ${data.nombre} 🎉`, 'ok', 4000);
        }
    } catch (e) {
        mostrarError('reg-error', 'Error de conexión con el servidor.');
    }
}

/** Cierra la sesión del usuario. */
async function ejecutarLogout() {
    await fetch('/api/logout', { method: 'POST' });
    document.getElementById('pantalla-auth').style.display = 'flex';
    document.getElementById('app-principal').style.display = 'none';
    // Limpiar campos de login
    document.getElementById('login-email').value    = '';
    document.getElementById('login-password').value = '';
    mostrarToast('Sesión cerrada correctamente.', 'info');
}


// =============================================
// 3. BÚSQUEDA POR CATEGORÍAS
// =============================================

/**
 * Cambia la categoría activa y muestra las plataformas correspondientes.
 * @param {HTMLElement} btn - Botón de categoría clickeado.
 */
function seleccionarCategoria(btn) {
    categoriaActual = btn.dataset.cat;

    // Actualizar estilos de tabs
    document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    // Mostrar bloque de plataformas de la categoría seleccionada
    ['Tecnología', 'Hogar', 'Moda'].forEach(cat => {
        const bloque = document.getElementById(`plat-${cat}`);
        if (bloque) bloque.style.display = (cat === categoriaActual) ? 'flex' : 'none';
    });
}

/**
 * Obtiene el valor del campo de búsqueda.
 * @returns {string}
 */
function obtenerValorProducto() {
    const el = document.getElementById('producto');
    return el ? el.value.trim() : '';
}

/**
 * Obtiene las plataformas seleccionadas (checkboxes marcados del grupo visible).
 * @returns {string[]}
 */
function obtenerPlataformasSeleccionadas() {
    const bloque = document.getElementById(`plat-${categoriaActual}`);
    if (!bloque) return [];
    const checks = bloque.querySelectorAll('input[type="checkbox"]:checked:not(:disabled)');
    return Array.from(checks).map(c => c.value);
}

/**
 * Valida los inputs de búsqueda antes de enviar.
 * @param {string} producto
 * @param {string[]} plataformas
 * @returns {boolean}
 */
function validarEntradas(producto, plataformas) {
    if (!producto) {
        mostrarToast('Ingresá un producto para rastrear.', 'error');
        return false;
    }
    if (plataformas.length === 0) {
        mostrarToast('Seleccioná al menos una plataforma.', 'error');
        return false;
    }
    return true;
}

/** Muestra un mensaje de carga animado en la tabla de resultados. */
function mostrarCarga(tablaId, colspan = 4) {
    const tabla = document.getElementById(tablaId);
    if (tabla) {
        tabla.innerHTML = `
            <tr class="cargando-row">
                <td colspan="${colspan}">
                    <span class="spinner"></span> Analizando precios en tiempo real...
                </td>
            </tr>`;
    }
}

/**
 * Ordena resultados por precio ascendente (los sin precio van al final).
 * @param {Object[]} resultados
 * @returns {Object[]}
 */
function ordenarPorPrecio(resultados) {
    return [...resultados].sort((a, b) => {
        if (!a.precio || a.precio <= 0) return  1;
        if (!b.precio || b.precio <= 0) return -1;
        return a.precio - b.precio;
    });
}

/**
 * Genera HTML de una fila para la tabla resumen.
 * @param {Object} item
 * @returns {string}
 */
function generarFilaResumen(item) {
    const disponible = item.precio && item.precio > 0;
    return `
        <tr>
            <td><span class="badge">${item.tienda}</span></td>
            <td>${disponible
                ? '<span class="badge-disponible">✔ Disponible</span>'
                : '<span class="badge-sinstock">✘ Sin Stock</span>'}</td>
            <td class="precio-cell">${disponible ? formatearPrecio(item.precio) : '-'}</td>
            <td>${disponible
                ? `<a href="${item.url_compra}" target="_blank" class="btn-ir-tienda">Ir a la Tienda ➔</a>`
                : '<span style="color:#bbb;">No disponible</span>'}</td>
        </tr>`;
}

/**
 * Genera HTML de una fila para la tabla de desglose completo.
 * @param {Object} item
 * @returns {string}
 */
function generarFilaDesglose(item) {
    const disponible = item.precio && item.precio > 0;
    return `
        <tr>
            <td><span class="badge">${item.tienda}</span></td>
            <td style="max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                title="${item.nombre_producto}">${item.nombre_producto}</td>
            <td class="precio-cell">${disponible ? formatearPrecio(item.precio) : '-'}</td>
            <td>${disponible
                ? `<a href="${item.url_compra}" target="_blank" class="btn-ir-tienda">Ver ➔</a>`
                : '<span style="color:#bbb;">No disponible</span>'}</td>
        </tr>`;
}

/**
 * Renderiza el historial completo de precios.
 * @param {Object[]} historial
 */
function renderizarHistorial(historial) {
    const tabla = document.getElementById('tabla-historial-completo');
    if (!historial || historial.length === 0) {
        tabla.innerHTML = '<tr><td colspan="3" class="td-placeholder">No hay registros previos.</td></tr>';
        return;
    }
    tabla.innerHTML = historial.map(r => `
        <tr>
            <td style="color:#777;">${r.fecha}</td>
            <td><strong>${r.tienda}</strong></td>
            <td class="precio-cell">${formatearPrecio(r.precio)}</td>
        </tr>`).join('');
}

/** Función principal: ejecuta el rastreo de precios. */
async function ejecutarRastreo() {
    const producto    = obtenerValorProducto();
    const plataformas = obtenerPlataformasSeleccionadas();

    if (!validarEntradas(producto, plataformas)) return;

    // Mostrar carga en tablas
    mostrarCarga('tabla-resultados', 4);
    mostrarCarga('tabla-desglose',   4);
    mostrarCarga('tabla-historial-completo', 3);

    // Ocultar botón de favorito mientras se carga
    document.getElementById('btn-favorito-container').style.display = 'none';

    try {
        const resp = await fetch('/api/rastrear', {
            method:  'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept':       'application/json'
            },
            body: JSON.stringify({
                producto,
                plataformas,
                categoria: categoriaActual
            })
        });

        const data = await resp.json();

        if (data.error) {
            mostrarToast(data.error, 'error');
            return;
        }

        // --- Guardar estado para uso en favoritos ---
        ultimaBusqueda = {
            producto_id: data.producto_id,
            producto:    data.producto,
            categoria:   data.categoria
        };

        // --- Tabla resumen (1 por plataforma, ordenado) ---
        const resumen = {};
        data.desglose.forEach(item => {
            if (!resumen[item.tienda] || (item.precio && item.precio < resumen[item.tienda].precio)) {
                resumen[item.tienda] = item;
            }
        });
        const ordenados = ordenarPorPrecio(Object.values(resumen));
        document.getElementById('tabla-resultados').innerHTML =
            ordenados.map(generarFilaResumen).join('') ||
            '<tr><td colspan="4" class="td-placeholder">Sin resultados.</td></tr>';

        // --- Tabla desglose completo ---
        document.getElementById('tabla-desglose').innerHTML =
            data.desglose.length > 0
                ? data.desglose.map(generarFilaDesglose).join('')
                : '<tr><td colspan="4" class="td-placeholder">No se encontraron productos.</td></tr>';

        // --- Historial ---
        renderizarHistorial(data.historial_completo);

        // --- Dashboard métricas ---
        const mejorOferta = ordenados.find(r => r.precio && r.precio > 0);
        document.getElementById('precio-minimo').textContent =
            mejorOferta ? formatearPrecio(mejorOferta.precio) : '$0';
        document.getElementById('tienda-barata').textContent =
            mejorOferta ? `Mejor oferta en ${mejorOferta.tienda}` : 'Sin resultados';
        document.getElementById('hist-min').textContent =
            data.historial_minimo_absoluto ? formatearPrecio(data.historial_minimo_absoluto) : '$0';
        document.getElementById('total-plataformas').textContent = ordenados.length;
        document.getElementById('stock-total').textContent =
            ordenados.filter(r => r.precio && r.precio > 0).length;

        // --- Mostrar botón guardar favorito ---
        if (ultimaBusqueda.producto_id) {
            document.getElementById('btn-favorito-container').style.display = 'block';
        }

        mostrarToast(`✅ Rastreo completado: ${data.producto}`, 'ok');

    } catch (e) {
        console.error('Error en rastreo:', e);
        mostrarToast('Error de comunicación con el servidor.', 'error');
    }
}


// =============================================
// 4. GESTIÓN DE FAVORITOS
// =============================================

/**
 * Guarda el producto de la última búsqueda en favoritos.
 * Llamado desde el botón "Guardar en Favoritos".
 */
async function guardarEnFavoritos() {
    if (!ultimaBusqueda.producto_id) {
        mostrarToast('Realizá una búsqueda primero.', 'error');
        return;
    }

    try {
        const resp = await fetch('/api/favoritos', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ producto_id: ultimaBusqueda.producto_id })
        });
        const data = await resp.json();

        if (data.error) {
            mostrarToast(
                data.error === 'El producto ya está en favoritos'
                    ? '⭐ Este producto ya está en tus favoritos.'
                    : data.error,
                'info'
            );
        } else {
            mostrarToast('❤️ Producto guardado en favoritos.', 'ok');
        }
    } catch (e) {
        mostrarToast('Error al guardar en favoritos.', 'error');
    }
}

/** Carga y renderiza la lista de favoritos del usuario. */
async function cargarFavoritos() {
    const contenedor = document.getElementById('lista-favoritos');
    contenedor.innerHTML = '<div class="empty-state"><div class="spinner" style="width:32px;height:32px;"></div></div>';

    try {
        const resp = await fetch('/api/favoritos');
        const data = await resp.json();

        if (data.error || !data.favoritos || data.favoritos.length === 0) {
            contenedor.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">❤️</div>
                    <p>No tenés favoritos guardados todavía.<br>
                    Buscá un producto y presioná <strong>Guardar en Favoritos</strong>.</p>
                </div>`;
            return;
        }

        contenedor.innerHTML = data.favoritos.map(fav => generarTarjetaFavorito(fav)).join('');

    } catch (e) {
        contenedor.innerHTML = '<div class="empty-state"><p>Error al cargar favoritos.</p></div>';
    }
}

/**
 * Genera el HTML de una tarjeta de favorito.
 * @param {Object} fav - Datos del favorito desde la API.
 * @returns {string}
 */
function generarTarjetaFavorito(fav) {
    const catSlug  = (fav.categoria || 'tecnologia').toLowerCase();
    const umbralVal = fav.umbral_precio ? fav.umbral_precio : '';

    return `
        <div class="fav-card fav-card-${catSlug}" id="fav-card-${fav.id}">
            <div class="fav-card-header">
                <div class="fav-card-nombre">${fav.nombre_producto}</div>
                <div class="fav-card-cat">${fav.categoria}</div>
            </div>

            <div class="fav-precios">
                <div class="fav-precio-item">
                    <span class="fav-precio-label">💰 Precio Actual</span>
                    <span class="fav-precio-valor">
                        ${fav.precio_actual ? formatearPrecio(fav.precio_actual) : 'Sin datos'}
                    </span>
                </div>
                <div class="fav-precio-item">
                    <span class="fav-precio-label">📉 Mínimo Histórico</span>
                    <span class="fav-precio-valor">
                        ${fav.precio_minimo_historico ? formatearPrecio(fav.precio_minimo_historico) : 'Sin datos'}
                    </span>
                </div>
            </div>

            <div style="font-size:13px;color:#777;margin-bottom:12px;font-weight:600;">
                🔔 Alerta cuando baje de:
            </div>
            <div class="fav-umbral-row">
                <input
                    type="number"
                    class="fav-umbral-input"
                    id="umbral-${fav.id}"
                    placeholder="Ej: 150000"
                    value="${umbralVal}"
                    min="0"
                >
                <button class="fav-umbral-btn" onclick="actualizarUmbral(${fav.id})">
                    Guardar Umbral
                </button>
            </div>

            <div class="fav-actions">
                <button class="fav-delete-btn" onclick="eliminarFavorito(${fav.id})">
                    🗑️ Eliminar
                </button>
            </div>
        </div>`;
}

/**
 * Actualiza el umbral de precio de un favorito.
 * @param {number} favoritoId
 */
async function actualizarUmbral(favoritoId) {
    const input  = document.getElementById(`umbral-${favoritoId}`);
    const umbral = parseFloat(input.value);

    if (!input.value || isNaN(umbral) || umbral <= 0) {
        mostrarToast('Ingresá un umbral de precio válido (mayor a 0).', 'error');
        return;
    }

    try {
        const resp = await fetch(`/api/favoritos/${favoritoId}/umbral`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ umbral_precio: umbral })
        });
        const data = await resp.json();
        if (data.ok) {
            mostrarToast(`🔔 Alerta configurada en ${formatearPrecio(umbral)}`, 'ok');
        } else {
            mostrarToast(data.error || 'Error al actualizar umbral.', 'error');
        }
    } catch (e) {
        mostrarToast('Error de conexión.', 'error');
    }
}

/**
 * Elimina un favorito de la lista.
 * @param {number} favoritoId
 */
async function eliminarFavorito(favoritoId) {
    try {
        const resp = await fetch(`/api/favoritos/${favoritoId}`, { method: 'DELETE' });
        const data = await resp.json();
        if (data.ok) {
            const card = document.getElementById(`fav-card-${favoritoId}`);
            if (card) card.remove();
            mostrarToast('Favorito eliminado.', 'info');
            // Si no quedan tarjetas, mostrar estado vacío
            const contenedor = document.getElementById('lista-favoritos');
            if (!contenedor.querySelector('.fav-card')) {
                contenedor.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❤️</div>
                        <p>No tenés favoritos guardados todavía.</p>
                    </div>`;
            }
        }
    } catch (e) {
        mostrarToast('Error al eliminar.', 'error');
    }
}


// =============================================
// 5. SISTEMA DE ALERTAS
// =============================================

/** Consulta al backend y muestra las alertas activas del usuario. */
async function verificarAlertas() {
    const contenedor = document.getElementById('lista-alertas');
    contenedor.innerHTML = `
        <div class="empty-state">
            <span class="spinner" style="width:32px;height:32px;"></span>
        </div>`;

    try {
        const resp = await fetch('/api/alertas/verificar');
        const data = await resp.json();

        if (data.error) {
            contenedor.innerHTML = '<div class="empty-state"><p>Error al verificar alertas.</p></div>';
            return;
        }

        if (!data.alertas || data.alertas.length === 0) {
            contenedor.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔔</div>
                    <p>No hay alertas activas en este momento.<br>
                    Establecé un umbral de precio en tus favoritos.</p>
                </div>`;
            return;
        }

        contenedor.innerHTML = data.alertas.map(a => `
            <div class="alerta-card">
                <div class="alerta-info">
                    <div class="alerta-nombre">🛍️ ${a.nombre_producto}</div>
                    <div class="alerta-precios">
                        <span class="alerta-precio-actual">
                            ✅ Precio actual: ${formatearPrecio(a.precio_actual)}
                        </span>
                        <span class="alerta-precio-umbral">
                            Tu umbral: ${formatearPrecio(a.umbral_precio)}
                        </span>
                    </div>
                </div>
                <div class="alerta-icono">🔔</div>
            </div>`).join('');

        mostrarToast(`🔔 ${data.alertas.length} alerta(s) activa(s) encontradas.`, 'ok', 4000);

    } catch (e) {
        contenedor.innerHTML = '<div class="empty-state"><p>Error de conexión.</p></div>';
    }
}


// =============================================
// 6. INICIALIZACIÓN AL CARGAR LA PÁGINA
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    // Verificar sesión activa
    verificarSesionInicial();

    // Permitir buscar presionando Enter en el campo de producto
    const inputProducto = document.getElementById('producto');
    if (inputProducto) {
        inputProducto.addEventListener('keydown', e => {
            if (e.key === 'Enter') ejecutarRastreo();
        });
    }
});
