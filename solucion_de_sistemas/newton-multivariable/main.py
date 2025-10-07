from ...utils.titulo import *
from ...utils.tabla import *
from ...utils.grafica import *

try:
    import numpy as np
except ImportError:
    print("El paquete numpy es obligatorio para correr este programa",
          "por favor instale el paquete utilizando el siguiente comando",
          "[py/python/python3] -m pip install numpy", sep="\n")
    exit()

from typing import Callable, Iterator, Self

#Programa para calcular la soulucion a un sistea de ecuacioes no lineales

class Transformacion:

    def __init__(self,
        f: Callable[[np.ndarray], np.ndarray], n: int
    ):
        self.func = f
        self.orden = n

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.func(x)

    def derivada_parcial(self,
        x: np.ndarray, i: int, delta: float = 0.001
    ) -> np.ndarray:
        vec = x.copy()
        y = self.func(vec)
        vec[i] += delta
        y_delta = self.func(vec)
        return (y_delta-y)/delta

    def jacobiano(self, x: np.ndarray) -> np.ndarray:
        gradientes = [self.derivada_parcial(x, i) for i in range(self.orden)]
        return np.column_stack(gradientes)

    @classmethod
    def convertir(cls, *funcs: Callable) -> Self:
        n = len(funcs)
        if not all(func.__code__.co_argcount == n for func in funcs):
            raise ValueError("los cantidad de argumentos de cada\
                funcion y la cantidad de funciones debe ser iguales")
        def wrapper(x: np.ndarray) -> np.ndarray:
            return np.array([funcs[i](*x) for i in range(n)])
        return cls(wrapper, n)

def raiz_multivariable(
    f: Transformacion,
    x0: np.ndarray,
    err: float,
    max_iter: int = 100
) -> Iterator[tuple[np.ndarray, float]]:
    act = x0
    it = 0

    while True:
        J = f.jacobiano(act)
        try:
            #delta = f(act)/np.linalg.det(J)
            delta = np.linalg.solve(J, f(act))
        except  np.linalg.LinAlgError:
            print("Error al resolver el sistema")
            return
        prev, act = act, act - delta
        err_act = np.linalg.norm(act-prev)
        yield act, float(err_act)
        it += 1
        if err_act <= err or it > max_iter:
            return

import time

def buscar_raiz(
    f: Transformacion,
    x0: np.ndarray,
    err: float,
    max_iter: int = 100
) -> np.ndarray:
    tabla = Tabla("xi", "xi+1", "error", minlen=20)
    print(tabla.encabezado())
    it = raiz_multivariable(f, x0, err, max_iter=max_iter)

    act = x0
    for sig, err_act in it:
        print(tabla.fila(act, sig, err_act))
        time.sleep(0.5)
        act = sig

    return act

if __name__ == "__main__":

    print("Programa para calcular la solucion a un sistema",
          "no lineal mediante el metodo de Newton-Raphson",
          "Ecuaciones:",
          "\tx^2+xy-10=0",
          "\ty+3xy^2-57=0",
          sep="\n"
    )

    f1 = lambda x,y: x**2 + x*y - 10
    f2 = lambda x,y: y + 3*x*(y**2) - 57

    grafica = Grafica(
        Vista(
            x_min = -2,
            x_max = 6,
            y_min=-4,
            y_max=4
        ),
        res = 50,
        dt = 2
    )

    grafica.cuadricula()
    grafica.ejes()

    grafica.ecuacion_implicita("f1", f1,
        Vista(x_min=-2, x_max=6, y_min=-4, y_max=4),
        color="blue"
    )

    grafica.ecuacion_implicita("f2", f2,
        Vista(x_min=-2, x_max=6, y_min=-4, y_max=4),
        color="red"
    )

    grafica.mostrar(block=False)
    grafica.pausar()

    np.set_printoptions(precision=4)

    f = Transformacion.convertir(f1,f2)

    raices = []

    print("Raiz Primer Cuadrante")
    raiz = buscar_raiz(f, np.array([1.5,3.5], dtype=np.float64), 0.000001)
    raices.append(raiz)
    print("\n")

    print("Raiz Primer Cuarto Cuadrante")
    raiz = buscar_raiz(f, np.array([4,-2], dtype=np.float64), 0.000001)
    raices.append(raiz)
    print("\n")

    for raiz in raices:
        grafica.punto("", raiz[0], raiz[1], color="green")
        grafica.pausar(0.5)

    grafica.pausar(10)

