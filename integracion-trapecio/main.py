from ..utils.equipo import *
from ..utils.ansi import *
from ..utils.menu import *
from ..utils.deps.np import *
from ..utils.deps.sympy import *

#<==============Implementacion de la regla del trapecio==================>

from typing import Callable

def integral_definida(
    f: Callable[[np.ndarray], np.ndarray],
    a: float,
    b: float,
    n: int
) -> float:
    """
    Realiza la integral definida de una funcion de 'a' a 'b'
    utilizando el metodo del trapecio compuesto
    """
    if n < 1: raise ValueError(
        "el numero de particiones debe ser mayor o igual a 1"
    )
    if a == b: return 0
    if a > b: a,b = b,a
    y = f(np.linspace(a, b, n+1))
    return ((b-a)/n)*(y[1:-1].sum()+(y[-1]+y[1])/2)

if __name__ == "__main__":

    from dataclasses import dataclass
    @dataclass
    class Estado:
        expr: sympy.Basic
        f: Callable[[np.ndarray], np.ndarray]
        n: int = 100

    def status(estado: Estado | None):
        if estado is None: return
        print(
            "Calculadora de Integrales: Metodo del Trapecio Compuesto",
            f"f(x) = {estado.expr}",
            f"n = {estado.n}",
            sep="\n"
        ) 

    def introducir_funcion(estado: Estado | None):
        global menu
        x = sympy.symbols("x")
        try:
            expr = sympy.sympify(input(menu.prompt).strip())
        except sympy.SympifyError as e:
            print(f"Expresion Invalida:\n{e}")
            input()
            return
        f = sympy.lambdify(x, expr, modules="numpy")
        if estado:
            estado.expr = expr
            estado.f = f
        else:
            menu.estado = Estado(expr, f)
            for opcion in menu.opciones:
                opcion.activa = True

    @Opcion.esperar_entrada
    @Opcion.requerir_estado
    def evaluar_integral(estado: Estado):
        try:
            a = float(input("a = "))
            b = float(input("b = "))
        except ValueError:
            print("Introduzca un numero!")
            return 
        I = integral_definida(estado.f, a, b, estado.n)
        print(f"Int(f,{a},{b}) = {I:.5f}")

    @Opcion.requerir_estado
    def modificar_particiones(estado: Estado):
        try:
            n = int(input(menu.prompt))
        except ValueError:
            print("Introduzca un entero")
            input()
            return
        if n < 1:
            print("Introduzca un entero positivo")
            input()
            return
        estado.n = n

    def salir(_):
        altscreen(False)
        exit()

    menu = Menu([
        Opcion("Introducir Funcion", introducir_funcion),
        Opcion("Evaluar Integral", evaluar_integral, activa = False),
        Opcion("Modificar No. Particiones", modificar_particiones, activa=False),
        Opcion("Salir", salir)],
        pre = status
    )

    altscreen(True)
    while True: menu.desplegar()
