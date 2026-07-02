# **SIRCP - Sistema de Rastreo de Precio (Prototipo)**

Sistema para el rastreo y análisis de precios, desarrollado con **Flask** y **MySQL**.

---

## 📌 **Requisitos previos**
- Python 3.8 o superior.
- MySQL instalado y en ejecución.
- Git (opcional, para clonar el repositorio).

---

## 🛠 **Instrucciones de instalación**

### 1. **Clonar el repositorio**
```bash
git clone https://github.com/WillHelm696/Sistema-de-rastreo-de-Precio-Prototipo.git
cd Sistema-de-rastreo-de-Precio-Prototipo
```

---

### 2. **Configurar la base de datos**
1. **Crear la base de datos**:
   - Abre tu cliente de MySQL (ej: MySQL Workbench, phpMyAdmin o terminal).
   - Ejecuta el archivo `sircp_db.sql` para crear la base de datos y las tablas necesarias:
     ```bash
     mysql -u Tu_Usuario -p sircp_db < sircp_db.sql
     ```
     *(Reemplaza `Tu_Usuario` con tu usuario de MySQL).*

2. **Configurar la conexión en `db_manager.py`**:
   - Abre el archivo `db_manager.py` y modifica la función de conexión para que coincida con tus credenciales de MySQL:
     ```python
     return mysql.connector.connect(
         host="localhost",
         user="Tu_Usuario",       # Reemplaza con tu usuario de MySQL
         password="Tu_Contraseña", # Reemplaza con tu contraseña
         database="sircp_db"      # Nombre de la base de datos
     )
     ```

---

### 3. **Configurar el entorno virtual**
1. **Crear el entorno virtual**:
   ```bash
   python3 -m venv venv
   ```

2. **Activar el entorno virtual**:
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---
### 4. **Ejecutar la aplicación**
```bash
python app.py
```
Abre tu navegador y ve a:
👉 [http://localhost:5000](http://localhost:5000)

---
### 5. **Desactivar el entorno virtual**
```bash
deactivate
```

---
---
## 📂 **Estructura del proyecto**
| Archivo/Carpeta       | Descripción                                  |
|-----------------------|----------------------------------------------|
| `app.py`              | Archivo principal de Flask.                  |
| `db_manager.py`       | Manejo de conexiones a la base de datos.     |
| `scraper_tools.py`    | Herramientas para el scraping de datos.      |
| `requirements.txt`    | Dependencias de Python.                      |
| `sircp_db.sql`        | Script para crear la base de datos.          |
| `static/`             | Archivos estáticos (CSS, JS, imágenes).      |
| `templates/`          | Plantillas HTML para Flask.                  |

---
---
## 🤝 **Contribuciones**
Si deseas contribuir, abre un *Pull Request* o reporta un *Issue* en el repositorio.

---
## 📜 **Licencia**
Este proyecto es de código abierto y está bajo la licencia **MIT**.
