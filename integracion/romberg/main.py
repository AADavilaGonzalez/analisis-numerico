from ...utils.equipo import *
from ...utils.deps.np import *
from ...utils.deps.sympy import *
from ...utils.ansi import *
from ...utils.menu import *

from typing import Callable

def integral_definida(
    f : Callable[[np.ndarray], np.ndarray],
    a : float,
    b : float,
    k : int
) -> float:
    """
    Implementacion del metodo de integracion de Romberg con iteraciones 'k' variable
    """
   
    if k < 1:
        raise ValueError("El numero de iteraciones debe ser mayor o igual a 1")

    if a == b: return 0

    signo = 1.0
    if a > b:
        signo = -1.0
        a,b = b,a

    def regla_del_trapecio(n : int) -> float:
        h = (b-a)/n
        y = f(np.linspace(a, b, n+1, dtype=float))
        return h*(y[1:-1].sum() + (y[0]+y[-1])/2)

    R = np.zeros((k,k), dtype=float)

    for i in range(k):
        R[i, 0] = regla_del_trapecio(2**i)

    p = 1
    for j in range(1,k):
        p *= 4
        for i in range(j,k):
            R[i,j] = (p*R[i,j-1]-R[i-1,j-1])/(p-1)

    return signo*R[k-1, k-1]


if __name__ == "__main__":

    class Estado: 

        def __init__(self, f: str, k: int = 5):
            self.f = f
            self.k = k
            self.pres = 5

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
                        dtype=float
                    )
            elif sympy_expr.free_symbols == {x}:
                f = sympy.lambdify(x, sympy_expr, modules="numpy")
            else:
                raise ValueError("la funcion debe depender solo de x")
            self._f = f
            self._expr = str(sympy_expr)

        @property
        def expr(self) -> str:
            return self._expr

        @property
        def k(self) -> int: return self._k

        @k.setter
        def k(self, val: int) -> None:
            if val < 1: raise ValueError("k debe ser mayor o igual a 1")
            self._k = val

        @property
        def pres(self): return self._pres

        @pres.setter
        def pres(self, val: int):
            if val < 0: raise ValueError("pres dene ser mayor o igual a 0")
            self._pres = val
        

    def estatus(estado: Estado | None):
        print("Calculadora de Integrales: Metodo de Romberg")
        if estado is None: return
        print(
            f"f(x) = {estado.expr}",
            f"k = {estado.k}",
            f"precision: {estado.pres} decimales",
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
        I = integral_definida(estado.f, a, b, estado.k)
        print(f"Int(f,{a},{b}) = {I:.{estado.pres}f}")

    @Opcion.requerir_estado
    def modificar_iteraciones(estado: Estado):
        try:
            k = int(input("n = "))
        except ValueError:
            print("Introduzca un entero")
            input()
            return
        if k < 1:
            print("el numero de iteraciones debe ser mayor o igual a 1")
            input()
            return
        estado.k = k

    @Opcion.requerir_estado
    def modificar_precision(estado : Estado):
        try:
            pres = int(input("precision = "))
        except ValueError:
            print("Introduzca un entero")
            input()
            return
        if pres < 0:
            print("la precision debe ser mayor o igual a 0")
            input()
            return
        estado.pres = pres

    def salir(_):
        altscreen(False)
        exit()

    menu = Menu([
        Opcion("Introducir Funcion", introducir_funcion),
        Opcion("Evaluar Integral", evaluar_integral, activa = False),
        Opcion("Modificar No. Iteraciones", modificar_iteraciones, activa = False),
        Opcion("Modificar Precision", modificar_precision, activa = False), 
        Opcion("Salir", salir)],
        pre = estatus
    )

    altscreen(True)
    while True: menu.desplegar()
