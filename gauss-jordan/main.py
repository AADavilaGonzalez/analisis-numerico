'''
Aldo Adrian Davila Gonzalez     1994122
Luis Fernando Segobia Torres    2177528
Roberto Sánchez Santoyo         2177547
'''

import re
try:
    import numpy as np
except ImportError:
    print("El paquete numpy es obligatorio para correr este programa",
          "por favor instale el paquete utilizando el siguiente comando",
          "[py/python/python3] -m pip install numpy", sep="\n")
    exit()

def parse_equation(eq, variables):

    izq, der = eq.split("=")
    der = float(der.strip())

    coef = [0.0] * len(variables)

    terminos = re.findall(r'([+-]?\d*\.?\d*)\s*(x_\d+)', izq.replace(" ", ""))

    for num, var in terminos:
        if num in ("", "+"):
            num = 1.0
        elif num == "-":
            num = -1.0
        else:
            num = float(num)
        coef[variables.index(var)] += num

    return coef, der

def gauss_jordan(
    A: np.ndarray,
    b: np.ndarray
) -> np.ndarray:

    # Implementacion del metodo de gauss jordan por medio de una matriz
    # aumentada. A debe ser una matriz cuadrada de nxn mientras que b
    # puede ser un solo vector de n elementos o una matriz de vectores
    # columna de nxm.
    if A.ndim != 2:
        raise ValueError("A debe ser una matriz")

    if A.shape[0] != A.shape[1]:
        raise ValueError("A debe ser una matriz cuadrada")

    n = A.shape[0]

    if b.ndim not in range(1,3):
        raise ValueError("b debe ser un vector o una matriz")

    if b.shape[0] != n:
        raise ValueError("El elemento a invertir\
            debe ser del mismo tamano que la matriz")

    b_view = b.reshape(n,1) if b.ndim == 1 else b
    Ab = np.hstack([A, b_view])


    #Eliminar Triangulo Inferior
    for i in range(0, n):

        if np.isclose(Ab[i,i], 0):
            for j in range(i+1, n):
                if not np.isclose(Ab[j,i], 0) :
                    Ab[[i,j], :] = Ab[[j,i], :]
                    break
            else:
                raise ValueError("se encontro una columna de ceros")

        for j in range(i+1, n):
            Ab[j] -= (Ab[j,i]/Ab[i,i]) * Ab[i]

    #Eliminar Triangulo Superior
    for i in range(n-1, 0, -1):
        for j in range(0, i):
            Ab[j] -= (Ab[j,i]/Ab[i,i]) * Ab[i]

    for i in range(n):
        Ab[i] /= Ab[i,i]

    return Ab[:, n:n+b_view.shape[1]].copy()


import os
match os.name:
    case "posix":
        clear = lambda: os.system("clear")
    case "nt":
        clear = lambda: os.system("os")
    case _:
        print("Que demonios viejo?!")
        exit()


if __name__ == "__main__":
    clear()
    print("Solucionador de Sistemas Lineales por Gauss-Jordan")
    n = 0 
    while True:
        try:
            n = int(input("Ingrese el numero de variables o ecuaciones de la matriz (n x n): "))
            if n > 0:
                variables = [f"x_{i+1}" for i in range(n)]
                break
            else:
                print("El tamaño debe ser un entero positivo.")
        except ValueError:
            print("Por favor, ingrese un número entero válido.")

    A = np.zeros((n, n), dtype=float)
    b = np.zeros((n, 1), dtype=float)

    print(f"\nIngrese las {n} ecuaciones del sistema (ejemplo: 2x_1 + 3x_2 - x_3 = 5):")
    for i in range(n):
        while True:
            eq = input(f"Ecuación {i+1}> ")
            try:
                coef, independiente = parse_equation(eq, variables)
                A[i] = coef
                b[i,0] = independiente
                break
            except ValueError:
                print("Error: Uno de los valores no es un número válido. Intente de nuevo.")

    print("\nResolviendo el sistema...")

    try:
        if np.linalg.det(A) == 0:
            print('La matriz tienen un det(A) = 0, por lo tanto el sistema de ecuaciones no tiene una solucion unica.')
            exit()
        solucion = gauss_jordan(A, b)
        print("\nLa solución del sistema es:")
        for i in range(n):
            print(f"x{i+1} = {solucion[i, 0]:.4f}")
    except ValueError as e:
        print(f"\nError al resolver el sistema: {e}")
        print("La matriz puede ser singular (no tener solución única).")
