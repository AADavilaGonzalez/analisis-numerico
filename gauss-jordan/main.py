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
    """
    Implementacion del metodo de gauss jordan por medio de una matriz
    aumentada. A debe ser una matriz cuadrada de nxn mientras que b
    puede ser un solo vector de n elementos o una matriz de vectores
    columna de nxm.
    """
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
            n_str = input("Ingrese el tamaño de la matriz (n x n): ")
            n = int(n_str)
            if n > 0:
                break
            else:
                print("El tamaño debe ser un entero positivo.")
        except ValueError:
            print("Por favor, ingrese un número entero válido.")

    print(f"\nIngrese las {n} ecuaciones del sistema.")
    print("Formato: a1 a2 ... an b (coeficientes y término constante, separados por espacios)")

    A = np.zeros((n, n), dtype=float)

    for i in range(n):
        while True:
            prompt = f"Fila {i+1}> "
            tokens: list[str] = input(prompt).split()

            if len(tokens) != n:
                print(f"Error: Se necesitan {n} coeficientes. Intente de nuevo.")
                continue
            
            try:
                A[i] = [float(token) for token in tokens]
                break
            except ValueError:
                print("Error: Uno de los valores no es un número válido. Intente de nuevo.")

    b = np.eye(n, dtype=float)

    inv = gauss_jordan(A,b)

    print("\nResolviendo el sistema...")

    try:
        solucion = gauss_jordan(A, b)
        print("\nLa solución del sistema es:")
        for i in range(n):
            print(f"x{i+1} = {solucion[i, 0]:.4f}")
    except ValueError as e:
        print(f"\nError al resolver el sistema: {e}")
        print("La matriz puede ser singular (no tener solución única).")
