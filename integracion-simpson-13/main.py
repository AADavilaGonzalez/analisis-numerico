from ..utils.titulo import *
from ..utils.ansi import *
from ..utils.menu import *
from ..utils.deps.np import *
from ..utils.deps.sympy import *

#<==============Implementacion de la regla simpson un tercio==================>

from typing import Callable

def integral_definida(
    f: Callable[[np.ndarray], np.ndarray],
    a: float,
    b: float,
    n: int
) -> float:
    """
    Realiza la integral definida de una funcion de 'a' a 'b'
    utilizando la regla de simpson un tercio compuesta
    """
    if n < 2: raise ValueError(
        "el numero de particiones debe ser mayor o igual a 2"
    )
    if n % 2 == 1: raise ValueError(
        "el numero de particiones debe ser un numero par"
    )

    if a == b: return 0
    if a > b: a,b = b,a

    y = f(np.linspace(a, b, n+1, dtype="float"))
    return ((b-a)/(3*n))*(
        y[0] +
        4*y[1:-1:2].sum() +
        2*y[2:-1:2].sum() +
        y[-1]
    )

if __name__ == "__main__":

    class Estado: 

        _f: Callable[[np.ndarray], np.ndarray]
        _expr: str
        _n: int = 100

        def __init__(self, f: str, n: int = 100):
            self.f = f
            self.n = n

        @property
        def f(self) -> Callable[[np.ndarray], np.ndarray]:
            return self._f

        @f.setter
        def f(self, expr: str):
            x = sympy.symbols("x")
            
            try:
                sympy_expr = sympy.sympify(expr)
            except sympy.SympifyError:
                raise ValueError("error de syntaxis")
            if not isinstance(sympy_expr, sympy.Expr):
                raise ValueError("no se pudo evaluar como expresion")

            if not sympy_expr.free_symbols:
                f = lambda x: np.full_like(
                        np.asarray(x),
                        float(sympy_expr),
                        dtype="float"
                    )
            elif sympy_expr.free_symbols == {x}:
                f = sympy.lambdify(x, sympy_expr, modules="numpy")
            else:
                raise ValueError("la funcion debe depender solo de x")
            self._f = f
            self._expr = str(sympy_expr)

        @property
        def expr(self) -> str:
            return str(self._expr)

        @property
        def n(self) -> int: return self._n

        @n.setter
        def n(self, val: int) -> None:
            self._n = val if val % 2 == 0 else val+1 
        

    def estatus(estado: Estado | None):
        print("Calculadora de Integrales: Regla de Simpson 1/3")
        if estado is None: return
        print(
            f"f(x) = {estado.expr}",
            f"n = {estado.n}",
            sep="\n"
        ) 

    def introducir_funcion(estado: Estado | None):
        global menu
        expr = input("f(x) = ")
        try:
            if estado:
                estado.f = expr
            else:
                menu.estado = Estado(expr)
                for opcion in menu.opciones:
                    opcion.activa = True
        except ValueError as e:
            print(e)
            input()
            return

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
            n = int(input("n = "))
        except ValueError:
            print("Introduzca un entero")
            input()
            return
        if n < 1:
            print("Introduzca un entero positivo")
            input()
            return
        if n % 2 == 1:
            n += 1
            print("Indice aumentado en uno, debe ser par")
            input()
        estado.n = n

    def salir(_):
        altscreen(False)
        exit()

    menu = Menu([
        Opcion("Introducir Funcion", introducir_funcion),
        Opcion("Evaluar Integral", evaluar_integral, activa = False),
        Opcion("Modificar No. Particiones", modificar_particiones, activa=False),
        Opcion("Salir", salir)],
        pre = estatus
    )

    altscreen(True)
    while True: menu.desplegar()
