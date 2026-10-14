# Directorio (Flask + MySQL) — Proyecto básico para principiantes

## Estructura del proyecto
```
directorio_app/
│
├── app.py              # Aplicación Flask (backend)
├── directorio.sql      # Script para crear la base de datos y tabla
├── requirements.txt    # Dependencias de Python
├── templates/
│   └── index.html      # Formulario + lista de contactos
└── static/
    └── style.css        # Estilos
```

## Pasos para ejecutarlo

### 1. Crear la base de datos
Abre MySQL (Workbench, phpMyAdmin o terminal) y ejecuta el
contenido del archivo `directorio.sql`. Esto crea la base
`directorio` y la tabla `contactos`.

### 2. Instalar las dependencias de Python
En una terminal, dentro de la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

### 3. Configurar la conexión a MySQL
Abre `app.py` y edita el diccionario `DB_CONFIG` con tu usuario
y contraseña de MySQL:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "tu_contraseña",
    "database": "directorio"
}
```

### 4. Ejecutar la aplicación

```bash
python app.py
```

### 5. Abrir en el navegador
Entra a: http://127.0.0.1:5000/

Ahí verás el formulario para agregar un contacto (nombre,
teléfono, correo) y la lista de contactos guardados en MySQL.

## Cómo funciona (resumen)
- `app.py` usa **Flask** para crear dos rutas:
  - `/` muestra el formulario y la lista de contactos (hace un
    `SELECT` a la base de datos).
  - `/agregar` recibe los datos del formulario por `POST` y
    hace un `INSERT` en la tabla `contactos`.
- `mysql-connector-python` es la librería que permite a Python
  hablar con MySQL.
- `index.html` usa **Jinja2** (el motor de plantillas de Flask)
  con `{{ }}` para mostrar datos y `{% %}` para bucles/condicionales.
- `style.css` solo da estilo visual, no afecta la lógica.
