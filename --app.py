# app.py
# ------------------------------------------------------
# Programa en Flask que se conecta a MySQL, crea la base
# de datos y tabla si no existen, y permite dar de alta
# registros en el directorio.
# ------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

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
    return render_template("index.html", contactos=contactos)


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


if __name__ == "__main__":
    inicializar_bd()  # Se asegura de que la BD y tabla existan
    app.run(debug=True)
