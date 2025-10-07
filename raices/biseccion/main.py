import math
from typing import Callable

FuncionReal = Callable[[float], float]

f: FuncionReal = lambda x : x*math.exp(x)-math.pi

def raicez_por_biseccion(
    f: FuncionReal,
    a: float,
    b: float,
    err: float = 0.000001
) -> float:

    if a > b:
        a,b = b,a

    if f(a) * f(b) > 0:
        raise ValueError(
            "Los valores del intervalo no cumplen con f(a)*f(b) < 0"
        )


    prev = a
    act = (b+a)/2

    print(f"{"a":^10} | {"b":^10} | {"xi":^10} | {"xi+1":^10} | {"error":^10}")
    print(f"{a:>10f} | {b:>10f} | {"NA":>10} | {act:>10f} | {"NA":>10}")

    while True:

        if f(act) > 0:
            b = act
        else:
            a = act

        err_act = math.fabs(act - prev)/act
        prev = act
        act = (b+a)/2

        print(f"{a:>10f} | {b:>10f} | {prev:>10f} | {act:>10f} | {err_act:>10f}")

        if  err_act <= err:
            break
    return act

x: float = raicez_por_biseccion(f, 0, 2)

print(  "El valor de la raiz de la funcion:",
        "f(x) = x*e^x-π",
        "en el intervalo [0,2] es de:",
        x,
        "con un error relativo de 0.000001",
        sep = "\n"
)
