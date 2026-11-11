#!/usr/bin/env python3
import sys
from datetime import date

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

for linea in sys.stdin:
    campos = linea.strip().split(",")

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
        print(f"{metodo}|{dia}\t{cantidad}")
