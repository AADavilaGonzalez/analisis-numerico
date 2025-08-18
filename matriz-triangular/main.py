"""
NOMBRE:     Aldo Adrian Davila Gonzalez
MATRICULA:  1994122
FECHA:      12-Agosto-2025
DESCRIPCION: PROGRAMA PARA CALCULA LAS SOLUCIONES A UN SISTEMA LINEAL
CON FORM A TRIANGULAR INFERIOR. SIGA LAS INSTRUCCIONES DEL PROGRAMA
"""

import random

Coeficientes = list[list[float]]
Constantes = list[float]


def imprimir_sistema(coef: Coeficientes, const: Constantes) -> None:
    PRES = 2

    n: int = len(coef)

    if n != len(const):
        raise ValueError

    lv = len(format(max([max(e) for e in coef]), f".{PRES}f")) + 1
    lx = len(str(n))
    lb = len(format(max(const), f".{PRES}f")) + 1

    for i in range(n):
        v = (
            " ".join([f"{e:{lv}.{PRES}f}" for e in coef[i]])
            + f" {0:{lv}d}" * (n-len(coef[i]))
        )
        x = f"x{i+1:{lx}d}"
        b = f"{const[i]:{lb}.{PRES}f}"

        if i == n//2:
            print(f"| {v} | x | {x} | = | {b} |")
        else:
            print(f"| {v} |   | {x} |   | {b} |")


def generar_sistema_aleatorio(n: int) -> tuple[Coeficientes, Constantes]:
    MIN = -100.0
    MAX = 100.0
    PRES = 2

    coef: list[list[float]] = []
    const: list[float] = []

    generar_numero = lambda : round(random.uniform(MIN, MAX), PRES)

    for i in range(n):
        coef.append([generar_numero() for _ in range(i+1)])
        const.append(generar_numero())

    return coef, const


def solucionar(coef: list[list[float]], const: list[float]) -> list[float]:

    sol: list[float] = []

    for i in range(len(coef)):
        x: float = const[i]
        for j in range(i):
            x -= coef[i][j]*sol[j]
        x /= coef[i][i]
        sol.append(x)

    return sol


if __name__ == "__main__":

    print(
        "Solucionador de Sistemas Lineales Triangulares Inferiores",
        "Ingrese las ecuaciones:",
        "a1(x1) + a2(x2) + ... + an(xn) = b",
        "Con el siguente formato:",
        "a1 a2 ... an b",
        "Introduzca una linea vacia para terminar con la captura",
        "o introduzca'RANDOM N' donde N es un numero entero",
        "para generar un sistema de N ecuaciones aleatorias",
        sep = "\n", end = "\n\n"
    )

    n: int = 0;
    rand: bool = False
    coef: list[list[float]] = []
    const: list[float] = []

    while True:
        tokens: list[str] = input("> ").split()

        if not tokens:
            break

        if tokens[0] == "RANDOM":
            try:
                n = int(tokens[1])
                rand = True
                break
            except ValueError:
                print("Introduzca un entero como argumento a RANDOM")
                continue

        if len(tokens) != n + 2:
            print(f"Se necesitan {n+2} valores para la ecuacion {n+1}")
            continue

        coef_ecuacion = []
        for i in range(n+1):
            try:
                coef_ecuacion.append(float(tokens[i]))
            except ValueError:
                print(f"El coeficiente {i+1} no se pudo interpretar",
                       "introduzca la ecuacion nuevamente", sep = "\n"
                )
                continue
        coef.append(coef_ecuacion)

        try:
            const.append(float(tokens[n+1]))
        except ValueError:
            print("El valor constante no se pudo interpretar",
                  "introduzca la ecuacion nuevamente", sep = "\n")

        n+=1

    print()

    if rand:
        coef, const = generar_sistema_aleatorio(n)

    sol: list[float] = solucionar(coef, const)

    print("Soluciones al sistema")
    imprimir_sistema(coef, const)

    digitos_n = len(str(n))
    for i in range(n):
        print(f"x{i+1:{digitos_n}} = {sol[i]:.4f}")

