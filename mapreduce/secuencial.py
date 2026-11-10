#!/usr/bin/env python3
from datetime import date

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
ARCHIVO = "/data/input/ventas_124050194.csv"
SALIDA = "/data/output/secuencial.txt"

totales = {}

with open(ARCHIVO, encoding="utf-8") as f:
    for linea in f:
        campos = linea.strip().split(",")

        # Misma lógica que el mapper: ignora encabezado y líneas mal formadas
        if len(campos) != 8 or campos[0] == "id":
            continue

        try:
            fecha = campos[1]
            cantidad = int(campos[5])
            metodo = campos[7].strip()
            dia = DIAS[date(int(fecha[0:4]), int(fecha[5:7]), int(fecha[8:10])).weekday()]
        except (ValueError, IndexError):
            continue

        if metodo:
            clave = f"{metodo}|{dia}"
            totales[clave] = totales.get(clave, 0) + cantidad

with open(SALIDA, "w", encoding="utf-8") as out:
    for clave in sorted(totales):
        out.write(f"{clave}\t{totales[clave]}\n")