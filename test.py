# NOMBRE:     Aldo Adrian Davila Gonzalez
# MATRICULA:  1994122
# FECHA:      01-10-2025
# FORMATO: El codigo pertinente a esta actividad se encuentra
# al final del archivo, delimitado por un comentario

"""
Tener las funciones escritas en este archivo en un buffer de texto 
puede causar problemas de indentacion en algunos editores debido a
las secuencias de escape
"""
def clear(): print("\033[H\033[2J", end="", flush=True)

def altscreen(set: bool):
    seq = "\033[?1049h" if set else "\033[?1049l"
    print(seq, end="", flush=True)


from typing import Callable, TypeVar, Generic, Iterator

__all__ = ["Accion", "Opcion", "Menu"]

T = TypeVar("T")

Accion = Callable[[T | None], None]
noOp: Accion = lambda _ : None

class Opcion(Generic[T]):

    def __init__(self,
        nombre: str,
        accion: Accion[T],
        *,
        activa: bool = True
    ):
        self.nombre = nombre
        self.accion = accion
        self.activa = activa

    @staticmethod
    def limpiar_pantalla(f: Accion[T]) -> Accion[T]:
        def wrapper(estado: T | None) -> None:
            clear()
            f(estado)
        return wrapper
            
    @staticmethod
    def esperar_entrada(f: Accion[T]) -> Accion[T]:
        def wrapper(estado: T | None) -> None:
            f(estado)
            input()
        return wrapper

    @staticmethod
    def requerir_estado(f: Callable[[T], None]) -> Accion[T]:
        def wrapper(estado: T | None) -> None:
            assert estado is not None
            f(estado)
        return wrapper

class Menu(Generic[T]):

    def __init__(self,
        opciones: list[Opcion[T]],
        estado: T | None = None,
        pre: Accion[T] = noOp,
        pos: Accion[T] = noOp,
        clear: bool = True,
        indices: bool = True,
        sangria: int = 0,
        prompt: str = "> ",
        val_inv: Accion[T] = noOp,
        sol_conf: Callable[[list[Opcion[T]]], Accion[T]] | None = None
    ):
        self.estado = estado
        self.opciones = opciones
        self.pre = pre
        self.pos = pos

        self.clear = clear

        self.indexable = indices
        self.mostrar_indices = indices

        self.sangria_ops = sangria
        self.sangria_prompt = sangria

        self.prompt = prompt

        self.val_inv = val_inv
        self.sol_conf = sol_conf or type(self).__solucionar_conflicto

    def __opciones_activas(self) -> Iterator[Opcion[T]]:
        return (op for op in self.opciones if op.activa)

    @staticmethod
    def __solucionar_conflicto(opciones: list[Opcion[T]]) -> Accion[T]:
        return opciones[0].accion


    def mostrar(self) -> None:
        if self.clear: clear()
        if self.pre: self.pre(self.estado)
        for i, opcion in enumerate(self.__opciones_activas()):
            linea = " " * self.sangria_ops
            if self.mostrar_indices:
                linea += f"{i+1}. "
            linea += opcion.nombre
            print(linea)
        if self.pos: self.pos(self.estado)


    def seleccionar(self) -> None:

        print(" " * self.sangria_prompt, end="")
        token = input(self.prompt).strip()
        if not token:
            self.val_inv(self.estado)
            return

        accion = None
        opciones_activas = tuple(self.__opciones_activas())

        if self.indexable and token.isdigit():
            i = int(token)
            if 1 <= i <= len(opciones_activas):
                accion = opciones_activas[i-1].accion
        else:  
            token = token.lower()
            candidatos = [
                op for op in opciones_activas
                if op.nombre.strip().lower().startswith(token)
            ]
            if len(candidatos) == 1:
                accion = candidatos[0].accion
            elif len(candidatos) != 0:
                accion = self.sol_conf(candidatos)

        if accion:
            accion(self.estado)
        else:
            self.val_inv(self.estado)


    def desplegar(self) -> None:
        self.mostrar()
        self.seleccionar()

    def desplegar_mientras(self, cond: Callable[[],bool]) -> None:
        while cond():
            self.mostrar()
            self.seleccionar()



try:
    import numpy as np
except ImportError:
    print("El paquete numpy es obligatorio para correr este programa",
            "por favor instale el paquete utilizando el siguiente comando",
            "[py/python/python3] -m pip install numpy", sep="\n")
    exit()


try:
    import sympy
except ImportError:
    print("El paquete sympy es obligatorio para correr este programa",
            "por favor instale el paquete utilizando el siguiente comando",
            "[py/python/python3] -m pip install sympy", sep="\n")
    exit()



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
    utilizando la regla de simpson tres octavos compuesta
    """
    if n < 2: raise ValueError(
        "el numero de particiones debe ser mayor o igual a 2"
    )
    if n % 3 != 0: raise ValueError(
        "el numero de particiones debe ser divisible por 3"
    )

    if a == b: return 0
    if a > b: a,b = b,a

    y = f(np.linspace(a, b, n+1, dtype="float"))
    return ((3*(b-a))/(8*n))*(
        y[0] +
        3*y[1:-1:3].sum() +
        3*y[2:-1:3].sum() +
        2*y[3:-1:3].sum() +
        y[-1]
    )

if __name__ == "__main__":

    class Estado: 

        _f: Callable[[np.ndarray], np.ndarray]
        _expr: str
        _n: int = 99

        def __init__(self, f: str, n: int = 99):
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
            remainder = val % 3
            self._n = val if remainder == 0 else val + (3 - remainder) 
        

    def status(estado: Estado | None):
        if estado is None: return
        print(
            "Calculadora de Integrales: Regla de Simpson 3/8",
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
        remainder = n % 3
        if remainder != 0:
            n += (3 - remainder)
            print("Indice ajustado, debe ser divisible por 3")
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
        pre = status
    )

    altscreen(True)
    while True: menu.desplegar()

