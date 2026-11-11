import os
import time

import psycopg2
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def run(sql, params=(), fetch=None):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            data = None
            if fetch == "all":
                data = cur.fetchall()
            elif fetch == "one":
                data = cur.fetchone()
        conn.commit()
        return data
    finally:
        conn.close()


def init_db():
    for _ in range(10):
        try:
            run("""
                CREATE TABLE IF NOT EXISTS resultados (
                    id SERIAL PRIMARY KEY,
                    metodo_pago TEXT NOT NULL,
                    dia_semana  TEXT NOT NULL,
                    unidades    BIGINT NOT NULL,
                    UNIQUE (metodo_pago, dia_semana)
                )
            """)
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a la base de datos")


@app.get("/")
def inicio():
    return jsonify({"mensaje": "API de ventas DataMart", "endpoints": ["/resultados"]})


#  todos los registros
@app.get("/resultados")
def listar():
    return jsonify(run("SELECT * FROM resultados ORDER BY metodo_pago, id", fetch="all"))


# > filtro por método de pago 
@app.get("/resultados/<metodo>")
def por_metodo(metodo):
    dia = request.args.get("dia")
    if dia:
        filas = run(
            "SELECT * FROM resultados WHERE metodo_pago ILIKE %s AND dia_semana ILIKE %s ORDER BY id",
            (metodo, dia), fetch="all")
    else:
        filas = run(
            "SELECT * FROM resultados WHERE metodo_pago ILIKE %s ORDER BY id",
            (metodo,), fetch="all")
    return jsonify(filas)


# > crea un registro
@app.post("/resultados")
def crear():
    d = request.get_json(silent=True) or {}
    try:
        metodo, dia, unidades = d["metodo_pago"], d["dia_semana"], int(d["unidades"])
    except (KeyError, ValueError):
        return jsonify({"error": "Se requiere metodo_pago, dia_semana y unidades (entero)"}), 400
    try:
        fila = run(
            "INSERT INTO resultados (metodo_pago, dia_semana, unidades) VALUES (%s, %s, %s) RETURNING *",
            (metodo, dia, unidades), fetch="one")
    except errors.UniqueViolation:
        return jsonify({"error": "Ya existe esa combinación de método de pago y día"}), 409
    return jsonify(fila), 201


# actualiza las unidades
@app.put("/resultados/<int:rid>")
def actualizar(rid):
    d = request.get_json(silent=True) or {}
    try:
        unidades = int(d["unidades"])
    except (KeyError, ValueError):
        return jsonify({"error": "Se requiere unidades (entero)"}), 400
    fila = run("UPDATE resultados SET unidades = %s WHERE id = %s RETURNING *",
               (unidades, rid), fetch="one")
    if not fila:
        return jsonify({"error": "No existe ese id"}), 404
    return jsonify(fila)


#  elimina un registro
@app.delete("/resultados/<int:rid>")
def borrar(rid):
    fila = run("DELETE FROM resultados WHERE id = %s RETURNING id", (rid,), fetch="one")
    if not fila:
        return jsonify({"error": "No existe ese id"}), 404
    return jsonify({"eliminado": rid})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
