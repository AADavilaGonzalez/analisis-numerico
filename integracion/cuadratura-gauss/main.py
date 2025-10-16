from ...utils.equipo import *
from ...utils.ansi import *
from ...utils.menu import *
from ...utils.deps.np import *
from ...utils.deps.sympy import *

#<==============Implementacion de la la cuadratura de Gauss==================>

from typing import Callable, cast

def integral_definida(
    f: Callable[[np.ndarray], np.ndarray],
    a: float,
    b: float,
    n: int
) -> float:
    """
    Realiza la integral definida de una funcion de 'a' a 'b'
    utilizando la cuadratura de Gauss-Legendre con 'n' puntos.
    """
    if n < 2: raise ValueError(
        "el numero de puntos debe ser mayor o igual a 2"
    )
    if a == b: return 0
    if a > b: a,b = b,a

    #Obtener los nodos y pesos para [-1, 1]
    nodos, pesos = np.polynomial.legendre.leggauss(n)

    #cambio de variable para mapear los nodos al intervalo [a, b]
    nodos_mapeados = 0.5 * (b - a) * nodos + 0.5 * (a + b)

    #Evaluar la funcion en los puntos mapeados
    valores_f = f(nodos_mapeados)

    #Calcular la integral usando la suma ponderada
    integral = 0.5 * (b - a) * np.sum(pesos * valores_f)
    
    return integral

if __name__ == "__main__":

    from dataclasses import dataclass
    @dataclass
    class Estado:
        expr: sympy.Basic
        f: Callable[[np.ndarray], np.ndarray]
        n: int = 5  

    def status(estado: Estado | None):
        if estado is None: return
        print(
            "Calculadora de Integrales: Cuadratura de Gauss", 
            f"f(x) = {estado.expr}",
            f"n = {estado.n} (puntos)",
            sep="\n"
        ) 

    def introducir_funcion(estado: Estado | None):
        global menu
        x = sympy.symbols("x")
        try:
            expr = sympy.sympify(input("f(x) = ").strip())
        except sympy.SympifyError as e:
            print(f"Expresion invalida:\n{e}")
            return

        if expr.free_symbols:
            if expr.free_symbols == {x}:
                f = sympy.lambdify(x, expr, modules="numpy")
            else:
                print("Ej. de f(x): x**2 - 2*x + 3.")
                input()
                return
        else:
            try:
                val = float(cast(float, expr))
                f = lambda x_val: np.full_like(
                    np.asarray(x_val),
                    val,
                    dtype="float"
                )
            except (ValueError, TypeError):
                print("La expresion constante debe ser un numero valido.")
                return

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
    def modificar_puntos(estado: Estado): 
        try:
            n = int(input("n = "))
        except ValueError:
            print("Introduzca un entero")
            input()
            return
        if n < 2:
            print("Introduzca un entero positivo >=2")
            input()
            return
        estado.n = n

    def salir(_):
        altscreen(False)
        exit()

    menu = Menu([
        Opcion("Introducir Funcion", introducir_funcion),
        Opcion("Evaluar Integral", evaluar_integral, activa = False),
        Opcion("Modificar No. Puntos", modificar_puntos, activa=False), 
        Opcion("Salir", salir)],
        pre = status
    )

    altscreen(True)
    while True: menu.desplegar()
