#!/usr/bin/env python3
import sys

actual = None
total = 0

for linea in sys.stdin:
    try:
        clave, valor = linea.rstrip("\n").split("\t")
        valor = int(valor)
    except ValueError:
        continue

    if clave == actual:
        total += valor
    else:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual = clave
        total = valor

if actual is not None:
    print(f"{actual}\t{total}")