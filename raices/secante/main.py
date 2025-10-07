from ...utils.titulo import *
from ...utils.tabla import *
from ...utils.viejo.tipos import *

#DESCRIPCION: programa para calcular las raices reales de dos
# funciones por medio del metodo del la secante modificada

import math
from typing import Iterator

def raiz_por_secante(
    f: FuncionReal,
    x0: float,
    err: float,
    dx: float = 0.01
) -> Iterator[tuple[float, float]]:

    act = x0
    while True:
        m_inv = dx/(f(act+dx)-f(act))
        prev, act = act, act - f(act)*m_inv
        err_act = math.fabs((act-prev)/act)
        yield act, err_act
        if err_act <= err:
            return

def buscar_raiz(
    f: FuncionReal,
    x0: float,
    err: float,
    dx: float = 0.01,
):

    tabla = Tabla("xi", "xi+1", "error")
    print(tabla.encabezado())
    act = x0
    iterador = raiz_por_secante(f,act,err,dx=dx)

    for sig, err_act in iterador:
        print(tabla.fila(act, sig, err_act))
        act = sig

if __name__ == "__main__":
    f1 = FuncionReal(lambda x: 3*x + 2*math.log(x))
    f2 = FuncionReal(lambda x: 2*x-1-(1000/math.pi)*(x**-2 + x**-3))
    ERROR = 0.000001

    print("Soluciones 3x + 2ln(x)")
    print("Tabla Raiz 1")
    buscar_raiz(f1, 1, ERROR)
    print()
    print("Tabla Raiz 2")
    buscar_raiz(f2, 2, ERROR)
    print()
    print("Solucion 2x-1-(1000/π)(x^-2 + x^-3)")
    buscar_raiz(f2, 3, ERROR)
