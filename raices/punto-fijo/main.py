from ...utils.tabla import *

import math
from typing import Callable

FuncionReal = Callable[[float], float]

f: FuncionReal = lambda x : math.exp(x)-math.pi*x

def raiz_por_punto_fijo(
    f: FuncionReal,
    x0: float,
    err: float = 0.000001
) -> float:

    g: FuncionReal = lambda x : f(x) + x

    prev = x0
    sig = g(prev)

    tabla = Tabla("xi", "xi+1", "error", minlen=10, floatpres=8)
    print(tabla.encabezado())

    while True:
        err_act = math.fabs(sig-prev)/sig
        print(tabla.fila(prev, sig, err_act))
        if err_act <= err:
            break
        prev = sig
        sig = g(prev)

    return sig


def conclusion(
    x0: float,
    err: float,
    raiz: float,
) -> str:
    return "\n".join([
        "El valor de la raiz de la funcion:",
        "f(x) = e^x-πx",
        f"cerca del punto inicial x={x0} es:",
        f"{raiz}",
        f"con un error relativo de {err}",
    ])


if __name__ == "__main__":

    x: float = raiz_por_punto_fijo(f, 0.6, 0.000001)
    print(conclusion(0.6, 0.000001, x))
