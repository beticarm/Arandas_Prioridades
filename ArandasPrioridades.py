from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
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

# =======================
# FORMULARIO
# =======================
@app.route("/", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        datos = (
            request.form["analista"],
            request.form["sistema"],
            request.form["numero_caso"],
            request.form["prioridad"],
            request.form["observaciones"],
            request.form["defino_3009"],
            request.form["atendido_fecha"]
        )

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO casos
            (analista, sistema, numero_caso, prioridad, observaciones, defino_3009, atendido_fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos)
        conn.commit()
        conn.close()

        return redirect(url_for("listar"))

    return render_template("formulario.html")

# =======================
# LISTA DE CASOS
# =======================
@app.route("/lista")
def listar():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos ORDER BY id DESC")
    casos = cursor.fetchall()
    conn.close()
    return render_template("Lista.html", registros=casos)

# =======================
# RESULTADOS (DETALLE)
# =======================
@app.route("/resultados/<int:id>")
def resultados(id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos WHERE id = ?", (id,))
    caso = cursor.fetchone()
    conn.close()
    return render_template("Resultados.html", caso=caso)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
