"""Agenda de Contactos - Flask + MySQL.
La base de datos y la tabla se crean solas al iniciar la app."""
import os
import re
import sys

import pymysql
from flask import Flask, abort, flash, redirect, render_template, request, url_for

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")  # XAMPP por defecto: sin contraseña
DB_NAME = os.environ.get("DB_NAME", "agenda_db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_conn(use_db=True):
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME if use_db else None,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def init_db():
    conn = get_conn(use_db=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cur.execute(f"USE `{DB_NAME}`")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS contactos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(120) NOT NULL,
                    telefono VARCHAR(20) DEFAULT NULL,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """
            )
            cur.execute("SELECT COUNT(*) AS n FROM contactos")
            if cur.fetchone()["n"] == 0:
                cur.executemany(
                    "INSERT INTO contactos (nombre, email, telefono) VALUES (%s, %s, %s)",
                    [
                        ("Ana Pérez", "ana@example.com", "3001234567"),
                        ("Carlos Gómez", "carlos@example.com", "3109876543"),
                    ],
                )
    finally:
        conn.close()


def query(sql, params=(), one=False, commit=False):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if commit:
                return cur.lastrowid
            return cur.fetchone() if one else cur.fetchall()
    finally:
        conn.close()


# ---------- Rutas ----------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        contactos = query(
            "SELECT * FROM contactos WHERE nombre LIKE %s OR email LIKE %s ORDER BY nombre",
            (like, like),
        )
    else:
        contactos = query("SELECT * FROM contactos ORDER BY nombre")
    return render_template("index.html", contactos=contactos, q=q)


@app.route("/contacto/nuevo", methods=["GET", "POST"])
@app.route("/contacto/<int:id>/editar", methods=["GET", "POST"])
def formulario(id=None):
    contacto = {"nombre": "", "email": "", "telefono": ""}
    if id:
        contacto = query("SELECT * FROM contactos WHERE id = %s", (id,), one=True)
        if not contacto:
            abort(404)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip() or None
        contacto = {"nombre": nombre, "email": email, "telefono": telefono or ""}

        if not nombre or not EMAIL_RE.match(email):
            flash("Nombre y correo válidos son obligatorios.", "error")
        else:
            if id:
                query(
                    "UPDATE contactos SET nombre=%s, email=%s, telefono=%s WHERE id=%s",
                    (nombre, email, telefono, id),
                    commit=True,
                )
            else:
                query(
                    "INSERT INTO contactos (nombre, email, telefono) VALUES (%s, %s, %s)",
                    (nombre, email, telefono),
                    commit=True,
                )
            flash("Contacto guardado correctamente.", "ok")
            return redirect(url_for("index"))

    return render_template("form.html", contacto=contacto, editando=bool(id))


@app.route("/contacto/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    query("DELETE FROM contactos WHERE id = %s", (id,), commit=True)
    flash("Contacto eliminado.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    try:
        init_db()
    except pymysql.err.OperationalError as e:
        sys.exit(
            f"\nNo se pudo conectar a MySQL ({e}).\n"
            "Verifica que MySQL esté iniciado en XAMPP y que usuario/contraseña sean correctos.\n"
        )
    app.run(debug=True, port=5001)
