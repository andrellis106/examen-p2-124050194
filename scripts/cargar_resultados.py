#!/usr/bin/env python3
import os
import sys

import psycopg2

ARCHIVO = sys.argv[1] if len(sys.argv) > 1 else "/data/output/resultado/part-00000"

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST", "db"),
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

cargados = 0
with conn, conn.cursor() as cur:
    # La tabla se crea si no existe (por ejemplo, tras borrar el volumen de la BD)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id SERIAL PRIMARY KEY,
            metodo_pago TEXT NOT NULL,
            dia_semana  TEXT NOT NULL,
            unidades    BIGINT NOT NULL,
            UNIQUE (metodo_pago, dia_semana)
        )
    """)

    with open(ARCHIVO, encoding="utf-8") as f:
        for linea in f:
            try:
                clave, total = linea.rstrip("\n").split("\t")
                metodo, dia = clave.split("|")
                total = int(total)
            except ValueError:
                continue  # línea mal formada: se salta

            # Si ya existe la combinación, actualiza (así se puede correr varias veces)
            cur.execute("""
                INSERT INTO resultados (metodo_pago, dia_semana, unidades)
                VALUES (%s, %s, %s)
                ON CONFLICT (metodo_pago, dia_semana)
                DO UPDATE SET unidades = EXCLUDED.unidades
            """, (metodo, dia, total))
            cargados += 1

conn.close()
print(f"Filas cargadas: {cargados}")