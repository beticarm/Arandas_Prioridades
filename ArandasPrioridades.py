from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import csv
from io import StringIO
from flask import Response


# Esto detecta automáticamente dónde está tu archivo .py y busca la carpeta templates ahí mismo
base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

DB_NAME = "casos.db"

def conectar_db():
    return sqlite3.connect(DB_NAME)

def crear_tabla():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS casos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analista TEXT,
        sistema TEXT,
        numero_caso TEXT,
        prioridad INTEGER,
        observaciones TEXT,
        defino_3009 TEXT,
        atendido_fecha TEXT
    )
    """)
    conn.commit()
    conn.close()

crear_tabla()

@app.route("/", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        # 1. Obtener todos los campos del formulario
        datos = request.form
        
        # 2. VALIDACIÓN: Verificar que ningún campo esté vacío
        campos_esperados = ["analista", "sistema", "numero_caso", "prioridad", "observaciones", "defino_3009", "atendido_fecha"]
        for campo in campos_esperados:
            valor = request.form.get(campo) # .get() devuelve None si no existe, no explota
            if not valor or not str(valor).strip():
                return f"Error: El campo '{campo}' es obligatorio.", 400

        # 3. Guardar en la base de datos si la validación pasó
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO casos 
                (analista, sistema, numero_caso, prioridad, observaciones, defino_3009, atendido_fecha)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datos["analista"],
                datos["sistema"],
                datos["numero_caso"],
                int(datos["prioridad"]),
                datos["observaciones"],
                datos["defino_3009"],
                datos["atendido_fecha"]
            ))
            conn.commit()
            conn.close()
            return redirect(url_for("listar"))
        except ValueError:
            return "Error: La prioridad debe ser un número entero.", 400

    return render_template("formulario.html")

@app.route("/lista")
def listar():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos ORDER BY id DESC")
    casos = cursor.fetchall()
    conn.close()
    return render_template("lista.html", registros=casos)

@app.route("/resultados/<int:id>")
def resultados(id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos WHERE id = ?", (id,))
    caso = cursor.fetchone()
    conn.close()
    return render_template("resultados.html", caso=caso)

@app.route("/exportar")
def exportar_csv():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos ORDER BY id DESC")
    registros = cursor.fetchall()
    columnas = [description[0] for description in cursor.description]
    conn.close()

    # Crear CSV en memoria
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(columnas)   # encabezados
    writer.writerows(registros) # datos

    # Preparar respuesta para descarga
    response = Response(
    output.getvalue().encode("utf-8-sig"),
    mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=casos.csv"

    return response
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar_db()
    cursor = conn.cursor()

    if request.method == "POST":
        datos = request.form

        cursor.execute("""
            UPDATE casos
            SET analista = ?,
                sistema = ?,
                numero_caso = ?,
                prioridad = ?,
                observaciones = ?,
                defino_3009 = ?,
                atendido_fecha = ?
            WHERE id = ?
        """, (
            datos["analista"],
            datos["sistema"],
            datos["numero_caso"],
            int(datos["prioridad"]),
            datos["observaciones"],
            datos["defino_3009"],
            datos["atendido_fecha"],
            id
        ))

        conn.commit()
        conn.close()
        return redirect(url_for("listar"))

    # GET → cargar datos existentes
    cursor.execute("SELECT * FROM casos WHERE id = ?", (id,))
    caso = cursor.fetchone()
    conn.close()

    return render_template("editar.html", caso=caso)
@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM casos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
