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
    n = 4

    A = np.array([[20, 30, 20, 50],
              [50, 40, 40, 20],
              [20, 10, 10, 20],
              [10, 20, 30, 10]], dtype=float)

    b = np.array([27, 39, 15, 19], dtype=float)


    print("\nResolviendo el sistema...")

    try:
        print("Matriz a resolver:\n")
        for i in range(len(b)):
            fila = " ".join(f"{A[i][j]:>6}" for j in range(len(b)))
            print(f"[{fila} | {b[i]:>6}]")
        if np.linalg.det(A) == 0:
            print('La matriz tienen un det(A) = 0, por lo tanto el sistema de ecuaciones no tiene una solucion unica.')
            exit()
        solucion = gauss_jordan(A, b)
        print("\nLa solución del sistema es:")
        for i in range(n):
            print(f"x{i+1} = {solucion[i, 0]:.4f}")
        print('Programa elaborado por:')
        print('Aldo Adrian Davila Gonzalez     1994122\nLuis Fernando Segobia Torres    2177528\nRoberto Sánchez Santoyo         2177547')

    except ValueError as e:
        print(f"\nError al resolver el sistema: {e}")
        print("La matriz puede ser singular (no tener solución única).")
