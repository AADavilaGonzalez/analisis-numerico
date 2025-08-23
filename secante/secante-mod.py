# NOMBRE:     Aldo Adrian Davila Gonzalez
# MATRICULA:  1994122
# FECHA:      12-Agosto-2025
# FORMATO: El codigo pertinente a esta actividad se encuentra
# al final del archivo, delimitado por un comentario

class Tabla:

    def __init__(self, *args:str, minlen=10, floatpres=6):
        self.campos = tuple(str(arg) for arg in args)
        campos_con_formato = tuple(campo.center(minlen) for campo in self.campos)
        self.espaciados = tuple(len(campo) for campo in campos_con_formato)
        self._encabezado = " | ".join(campos_con_formato)
        self.floatpres = floatpres

    def encabezado(self) -> str:
        return self._encabezado

    def fila(self, *args) -> str:

        def formatear(arg, l:int):
            match arg:
                case int():
                    return f"{arg:{l}d}"
                case float():
                    return f"{arg:{l}.{self.floatpres}f}"
                case _:
                    return str(arg)[:l].rjust(l)

        if len(args) != len(self.campos):
            raise ValueError("Provea la cantidad de argumentos conforme a los campos")
        celdas = [formatear(args[i], self.espaciados[i]) for i in range(len(args))]
        return " | ".join(celdas)


#DESCRIPCION: programa para calcular las raices reales de dos
# funciones por medio del metodo del la secante modificada

import math
from typing import Callable, Iterator

FuncionReal = Callable[[float], float]

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
    f1 = lambda x: 3*x + 2*math.log(x)
    f2 = lambda x: 2*x-1-(1000/math.pi)*(x**-2 + x**-3)
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

