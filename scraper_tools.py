from bs4 import BeautifulSoup

import requests
import time

def formatear_producto(producto,caracter):
    """Reemplaza los espacios por '+' o '%' para búsquedas."""
    return producto.replace(" ", caracter)


def scrap_fravega(producto):
    url = f"https://www.fravega.com/l/?keyword={formatear_producto(producto, '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        productos = soup.find_all("div", class_="sc-87b0945d-0")

        resultados = []
        for producto_div in productos[:5]:
            nombre_producto = producto_div.find("span", class_="sc-1fa74e6c-0").text.strip()
            vendedor = producto_div.find("p", class_="sc-82405aa0-0").text.strip()

            # Extraer precio
            precio_div = producto_div.find("div", {"data-test-id": "product-price"})
            precio = precio_div.find("span", class_="sc-1d9b1d9e-0").text.strip() if precio_div else "No disponible"

            # Extraer URL del producto
            enlace = producto_div.find('a', href=True)
            print(enlace)
            url_producto = f"https://www.fravega.com{enlace['href']}" if enlace else url

            resultados.append({
                "tienda": "Fravega",
                "nombre_producto": nombre_producto,
                "precio": precio,
                "url": url_producto
            })
        return resultados
    except Exception as e:
        print(f"Error en Web Scraping (Fravega): {e}")
        return []

# --- OnCity ---
def scrap_oncity(producto):
    url = f"https://www.oncity.com/{formatear_producto(producto, '%20')}?_q={formatear_producto(producto, '%20')}&map=ft"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        # Buscar todos los artículos de productos
        productos = soup.find_all("article", class_="vtex-product-summary-2-x-element")

        resultados = []
        for producto_div in productos[:5]:
            # Nombre del producto
            nombre_producto = producto_div.find("span", class_="vtex-product-summary-2-x-productBrand").text.strip()

            # Precio de venta (precio con descuento)
            precio_venta_span = producto_div.find("span", class_="vtex-product-price-1-x-sellingPriceValue")
            precio_venta = precio_venta_span.text.strip().replace("$", "").replace(".", "").replace(",", ".").replace("\xa0", "") if precio_venta_span else "No disponible"

            # Precio de lista (precio original)
            #precio_lista_span = producto_div.find("span", class_="vtex-product-price-1-x-listPriceValue")
            #precio_lista = precio_lista_span.text.strip().replace("$", "").replace(".", "").replace(",", ".").replace("\xa0", "") if precio_lista_span else "No disponible"

            # Precio sin impuestos
            #precio_sin_impuestos_span = producto_div.find("p", class_="aremsaprod-store-theme-14-x-priceWithoutTax")
            #precio_sin_impuestos = precio_sin_impuestos_span.text.strip().replace("Precio Sin Impuestos Nacionales $", "").replace(".", "").replace(",", ".") if precio_sin_impuestos_span else "No disponible"

            # URL del producto
            enlace = producto_div.find("a", href=True)
            url_producto = f"https://www.oncity.com{enlace['href']}" if enlace else "#"

            # Vendedor
            vendedor = producto_div.find("span", class_="aremsaprod-store-theme-14-x-sellerNameStrong").text.strip() if producto_div.find("span", class_="aremsaprod-store-theme-14-x-sellerNameStrong") else "OnCity"

            resultados.append({
                "tienda": vendedor,
                "nombre_producto": nombre_producto,
                "precio": precio_venta,
                #"precio_lista": precio_lista,
                #"precio_sin_impuestos": precio_sin_impuestos,
                "url": url_producto
            })
        return resultados
    except Exception as e:
        print(f"Error en Web Scraping (OnCity): {e}")
        return []

# --- Naldo ---
def scrap_naldo(producto):
    url = f"https://www.naldo.com.ar/{formatear_producto(producto, '%20')}?_q={formatear_producto(producto, '%20')}&map=ft"
    #url = f"https://www.naldo.com.ar/search/?q={formatear_producto(producto, '%')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Buscar todos los contenedores de productos
        productos = soup.find_all("div", class_="naldoar-search-result-3-x-galleryItem")

        resultados = []
        for producto_div in productos[:5]:
            # Buscar el contenedor del producto dentro del galleryItem
            section = producto_div.find("section", class_="vtex-product-summary-2-x-container")
            if not section:
                continue

            # Nombre del producto
            nombre_producto = section.find("span", class_="vtex-product-summary-2-x-productBrand").text.strip()

            # Precio de venta
            precio_venta_span = section.find("span", class_="vtex-product-price-1-x-sellingPriceValue")
            precio_venta = precio_venta_span.text.strip().replace("$", "").replace(".", "").replace(",", ".").replace("\xa0", "") if precio_venta_span else "No disponible"
            """
            # Precio de lista
            precio_lista_span = section.find("span", class_="vtex-product-price-1-x-listPriceValue")
            precio_lista = precio_lista_span.text.strip().replace("$", "").replace(".", "").replace(",", ".").replace("\xa0", "") if precio_lista_span else "No disponible"

            # Precio sin impuestos
            precio_sin_impuestos_span = section.find("p", class_="naldoar-store-component-1-x-textoTransparencia")
            precio_sin_impuestos = precio_sin_impuestos_span.text.strip().replace("Precio sin Impuestos Nacionales $", "").replace(".", "").replace(",", ".") if precio_sin_impuestos_span else "No disponible"

            # Descuento
            descuento_span = section.find("span", class_="vtex-product-price-1-x-savingsPercentage")
            descuento = descuento_span.text.strip() if descuento_span else "0%"
            """
            # URL del producto
            enlace = section.find("a", href=True)
            url_producto = f"https://www.naldo.com.ar{enlace['href']}" if enlace else "#"

            resultados.append({
                "tienda": "Naldo",
                "nombre_producto": nombre_producto,
                "precio": precio_venta,
                #"precio_lista": precio_lista,
                #"precio_sin_impuestos": precio_sin_impuestos,
                #"descuento": descuento,
                "url": url_producto
            })
        return resultados
    except Exception as e:
        print(f"Error en Web Scraping (Naldo): {e}")
        return []

# --- FGStore ---
def scrap_fgstore(producto):
    url = f"https://www.fgstore.com.ar/search/?q={formatear_producto(producto,'%')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        productos = soup.find_all("a", class_="product-item-link")

        resultados = []
        for producto_a in productos[:5]:
            nombre_producto = producto_a.find("div", class_="js-item-name").text.strip()
            precio_span = producto_a.find("span", class_="js-price-display")
            
            # --- CORRECCIÓN AQUÍ ---
            precio_str = precio_span.text.strip() if precio_span else "0"
            
            # Limpieza: quitamos el '$', quitamos los puntos de miles, 
            # y reemplazamos la coma decimal por un punto para convertir a float
            precio_limpio = precio_str.replace("$", "").replace(".", "").replace(",", ".")
            
            try:
                precio_float = float(precio_limpio)
                # Opcional: Si el sitio web a veces incluye centavos decimales que 
                # no quieres (ej: 9999.00), puedes redondearlo a int:
                precio_final = f"{int(precio_float):,}".replace(",", ".")
            except ValueError:
                precio_final = "No disponible"
            # -----------------------

            url_producto = producto_a["href"] if producto_a.has_attr("href") else "#"

            resultados.append({
                "tienda": "FGStore",
                "nombre_producto": nombre_producto,
                "precio": precio_final,
                "url": url_producto
            })
        return resultados
    except Exception as e:
        print(f"Error en Web Scraping (FGStore): {e}")
        return []

# --- Megatone ---
def _formatear_precio_arg(monto):
    """
    Convierte un número (ej: 459999 o 459999.99) al formato de texto que
    espera app.py: miles con punto y decimales con coma (ej: "459.999,99"
    o "459.999"). Es necesario porque Doofinder devuelve el precio como
    número JSON, no como texto con formato argentino como hacen las
    páginas que sí scrapeamos por HTML (Fravega, OnCity, etc.).
    """
    if monto is None:
        return "No disponible"
    try:
        monto = float(monto)
    except (ValueError, TypeError):
        return "No disponible"

    entero = int(monto)
    centavos = round((monto - entero) * 100)
    parte_entera = f"{entero:,}".replace(",", ".")

    if centavos:
        return f"{parte_entera},{centavos:02d}"
    return parte_entera


def scrap_megatone(producto):
    """
    Scraper para Megatone — vía la API de Doofinder (NO por HTML).

    DIAGNÓSTICO COMPLETO (ya resuelto, después de varias pruebas):
    Megatone usa Doofinder como motor de búsqueda. La página de
    resultados HTML llega vacía (un <div id="search-result"></div> sin
    nada adentro); un componente Vue la llena después, llamando desde el
    navegador a esta API pública (sin token secreto, confirmado en el
    código fuente real de Megatone: ResultadosBusqueda.vue):

        https://us1-search.doofinder.com/6/{hashId}/_search?query=...

    El hashId de Megatone es fijo: "7d78864dfd68192d967ce98f7af00970".
    Por eso pegamos directo a esa API en vez de parsear HTML: es más
    simple y más confiable que un scraper de BeautifulSoup.

    SI EN EL FUTURO ESTO VUELVE A FALLAR: probablemente Megatone cambió
    de proveedor de búsqueda o de hashId. Los prints de abajo (status,
    cantidad de resultados, fragmento de la respuesta cruda) te van a
    decir exactamente qué pasó, en vez de fallar en silencio.
    """
    HASH_ID = "7d78864dfd68192d967ce98f7af00970"
    url = f"https://us1-search.doofinder.com/6/{HASH_ID}/_search"
    params = {
        "page": 1,
        "rpp": 5,
        "query": producto
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.megatone.net/",
        "Origin": "https://www.megatone.net",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"[Megatone/Doofinder] status={response.status_code} largo={len(response.text)}")

        data = response.json()
        items = data.get("results", [])

        if not items:
            print(f"[Megatone/Doofinder] 0 resultados para '{producto}'. "
                  f"Respuesta cruda (primeros 300 caracteres): {response.text[:300]}")
            return []

        resultados = []
        for p in items[:5]:
            # esSeller: productos de marketplace (otro vendedor) traen
            # menos campos de precio en el JSON de Doofinder.
            es_seller = "sellers" in (p.get("df_grouping_id") or "")
            if es_seller:
                continue

            nombre_producto = p.get("title", producto)
            precio_numerico = p.get("best_price") or p.get("price")
            precio = _formatear_precio_arg(precio_numerico)
            url_producto = p.get("link", "#")

            resultados.append({
                "tienda": "Megatone",
                "nombre_producto": nombre_producto,
                "precio": precio,
                "url": url_producto
            })
        return resultados

    except Exception as e:
        print(f"Error en Web Scraping (Megatone): {e}")
        return []