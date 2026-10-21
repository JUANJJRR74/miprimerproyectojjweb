# app.py
# ------------------------------------------------------
# Programa en Flask que se conecta a MySQL, crea la base
# de datos y tabla si no existen, y permite dar de alta
# registros en el directorio.
# Además permite consultar contactos por nombre y generar
# un reporte en PDF con los resultados.
# ------------------------------------------------------
# comentario comit repositorio

# comentario dos

# comentario tres
# comentario 4 

import io
from datetime import datetime
from xml.sax.saxutils import escape

from flask import (Flask, render_template, request, redirect, url_for,
                   abort, send_file)
import mysql.connector
from mysql.connector import Error

# --- Librería para generar PDF (instalar con: pip install reportlab) ---
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)

app = Flask(__name__)

# ------------------------------------------------------
# DATOS DE CONEXIÓN A MYSQL
# ------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "coram",
    "password": "coramadministrador2008",
    "database": "directorio"
}


def inicializar_bd():
    """Crea la base de datos y la tabla si no existen."""
    try:
        conexion = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conexion.cursor()
        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS directorio")
        cursor.execute("USE directorio")
        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contactos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20),
                correo VARCHAR(100),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conexion.commit()
        cursor.close()
        conexion.close()
        print("Base de datos y tabla listas.")
    except Error as e:
        print(f"Error al inicializar la BD: {e}")


def obtener_conexion():
    """Crea y devuelve una conexión a la base de datos MySQL."""
    conexion = mysql.connector.connect(**DB_CONFIG)
    return conexion


@app.route("/")
def index():
    """Página principal: formulario y lista de registros."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contactos ORDER BY id DESC")
    contactos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("index.html", contactos=contactos, contacto_editar=None)


@app.route("/editar/<int:id>")
def editar(id):
    """Selecciona un contacto y lo carga en el formulario para modificarlo."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Contacto seleccionado
    cursor.execute("SELECT * FROM contactos WHERE id = %s", (id,))
    contacto_editar = cursor.fetchone()

    # Lista completa (para seguir mostrando la tabla)
    cursor.execute("SELECT * FROM contactos ORDER BY id DESC")
    contactos = cursor.fetchall()

    cursor.close()
    conexion.close()

    if contacto_editar is None:
        abort(404)  # el id no existe

    return render_template("index.html", contactos=contactos,
                           contacto_editar=contacto_editar)


@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    """Guarda los cambios del contacto seleccionado (UPDATE)."""
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sql = "UPDATE contactos SET nombre = %s, telefono = %s, correo = %s WHERE id = %s"
    cursor.execute(sql, (nombre, telefono, correo, id))
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(url_for("index"))


@app.route("/agregar", methods=["POST"])
def agregar():
    """Inserta un nuevo registro en la tabla contactos."""
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sql = "INSERT INTO contactos (nombre, telefono, correo) VALUES (%s, %s, %s)"
    valores = (nombre, telefono, correo)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(url_for("index"))


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    """Elimina de la tabla el contacto con el id recibido (DELETE)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sql = "DELETE FROM contactos WHERE id = %s"
    cursor.execute(sql, (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(url_for("index"))


# ------------------------------------------------------
# REPORTE EN PDF (consulta por nombre)
# ------------------------------------------------------
def construir_pdf(contactos, nombre_buscado):
    """
    Recibe la lista de contactos (diccionarios) y el texto buscado,
    y devuelve un objeto BytesIO con el PDF generado en memoria.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="Reporte de contactos", author="Directorio de Contactos"
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloReporte", parent=estilos["Title"],
        textColor=colors.HexColor("#2c3e50"), fontSize=22, spaceAfter=6)
    estilo_info = ParagraphStyle(
        "InfoReporte", parent=estilos["Normal"],
        textColor=colors.HexColor("#555555"), fontSize=10, leading=14)
    estilo_celda = ParagraphStyle(
        "CeldaReporte", parent=estilos["Normal"], fontSize=9, leading=11)

    criterio = escape(nombre_buscado) if nombre_buscado else "(todos los contactos)"
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    historia = [
        Paragraph("Reporte de contactos", estilo_titulo),
        Paragraph(f"<b>Criterio de búsqueda (nombre):</b> {criterio}", estilo_info),
        Paragraph(f"<b>Fecha de generación:</b> {fecha}", estilo_info),
        Paragraph(f"<b>Total de registros encontrados:</b> {len(contactos)}",
                  estilo_info),
        Spacer(1, 16),
    ]

    if contactos:
        # Encabezado de la tabla
        datos = [["ID", "Nombre", "Teléfono", "Correo", "Registro"]]
        for c in contactos:
            registro = c["fecha_registro"]
            registro_txt = registro.strftime("%d/%m/%Y") if registro else ""
            datos.append([
                str(c["id"]),
                # Paragraph permite que el texto largo salte de línea
                Paragraph(escape(c["nombre"] or ""), estilo_celda),
                Paragraph(escape(c["telefono"] or ""), estilo_celda),
                Paragraph(escape(c["correo"] or ""), estilo_celda),
                registro_txt,
            ])

        tabla = Table(
            datos, repeatRows=1,  # repite el encabezado en cada página
            colWidths=[0.5 * inch, 1.9 * inch, 1.2 * inch, 2.2 * inch, 0.9 * inch])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f2f2f2")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph(
            "No se encontraron contactos que coincidan con la búsqueda.",
            estilos["Normal"]))

    def pie_de_pagina(canvas, documento):
        """Dibuja el número de página al pie de cada hoja."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch,
                               f"Página {documento.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
    buffer.seek(0)
    return buffer


@app.route("/reporte")
def reporte():
    """
    Consulta los contactos cuyo nombre contenga el texto recibido
    (parámetro ?nombre=...) y devuelve un PDF con el resultado.
    Si el texto viene vacío, el reporte incluye todos los contactos.
    """
    nombre = request.args.get("nombre", "").strip()

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    # LIKE con comodines %: busca coincidencias parciales.
    # Se usa un parámetro (%s) para evitar inyección SQL.
    cursor.execute(
        "SELECT * FROM contactos WHERE nombre LIKE %s ORDER BY nombre ASC",
        (f"%{nombre}%",)
    )
    contactos = cursor.fetchall()
    cursor.close()
    conexion.close()

    pdf = construir_pdf(contactos, nombre)
    nombre_archivo = f"reporte_contactos_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    return send_file(pdf, mimetype="application/pdf",
                     as_attachment=False, download_name=nombre_archivo)


if __name__ == "__main__":
    inicializar_bd()  # Se asegura de que la BD y tabla existan
    app.run(debug=True)
