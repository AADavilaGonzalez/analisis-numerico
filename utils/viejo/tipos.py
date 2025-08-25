from .vector import *
from typing import Callable

class FuncionReal:
    DELTA = 0.0001

    def __init__(self, func: Callable[[float], float]):
        self._func = func

    @property
    def dim_entrada(self) -> int:
        return 1

    @property
    def dim_salida(self) -> int:
        return 1

    def __call__(self, x: float) -> float:
        return self._func(x)

    def derivada(self, x: float, delta: float = DELTA) -> float:
        return (self._func(x+delta)-self._func(x))/delta

class FuncionParametrica:
    DELTA = 0.001
    def __init__(self, func: Callable[[float], Vector], m):
        self._func = func
        self._dim_salida = m

    @property
    def dim_entrada(self) -> int:
        return 1

    @property
    def dim_salida(self) -> int:
        return self._dim_salida

    def __call__(self, x: float) -> Vector:
        return self._func(x)

    def derivada(self, x: float, delta: float = DELTA) -> Vector:
        return (self._func(x+delta)-self._func(x))/delta

    @classmethod
    def vectorizar(cls, *funcs: FuncionReal) -> Self:
        def func_vectorizada(x: float) -> Vector:
            return Vector([func(x) for func in funcs])
        return cls(func_vectorizada, len(funcs))

class FuncionEscalar():
    DELTA = 0.001

    def __init__(self, func: Callable[[Vector], float], n):
        self._func = func
        self._dim_entrada = n

    @property
    def dim_entrada(self) -> int:
        return self._dim_entrada

    @property
    def dim_salida(self) -> int:
        return 1

    def __call__(self, x: Vector) -> float:
            return self._func(x)

    def derivada_parcial(self, x: Vector, i: int, delta: float = DELTA) -> float:
        vec = x.copiar()
        y = self._func(vec)
        vec[i] += delta
        y_prima = self._func(vec)
        return (y_prima-y)/delta

    @classmethod
    def convertir(cls, func: Callable, n: int) -> Self:
        if n != func.__code__.co_argcount:
            raise ValueError(f"la funcion necesita {n} argumentos posicionales")
        def wrapper(x: Vector) -> float:
            return func(*(x._x))
        return cls(wrapper, n)

class FuncionVectorial:
    DELTA = 0.001
    def __init__(self, func: Callable[[Vector], Vector], n, m):
        self._func = func
        self._dim_entrada = n
        self._dim_salida = m

    @property
    def dim_entrada(self) -> int:
        return self._dim_entrada

    @property
    def dim_salida(self) -> int:
        return self._dim_salida

    def __call__(self, x: Vector) -> Vector:
        return self._func(x)

    def derivada_parcial(self, x: Vector, i:int, delta: float = DELTA) -> Vector:
        vec = x.copiar()
        y = self._func(vec)
        vec[i] += delta
        y_prima = self._func(vec)
        return (y_prima-y)/delta

    @classmethod
    def vectorizar(cls, *funcs: FuncionEscalar) -> Self:
        if not funcs:
            raise ValueError("se requiere al menos una funcion escalar")
        n = funcs[0]._dim_entrada
        if not all(funcs[i]._dim_entrada == n for i in range(1, len(funcs))):
            raise ValueError(
                f"todas las funciones deben la misma dimension de entrada"
            )
        def func_vectorizada(x: Vector) -> Vector:
            return Vector([func(x) for func in funcs])
        return cls(func_vectorizada, n, len(funcs))

    @classmethod
    def convertir(cls, func: Callable, n: int, m: int) -> Self:
        if n != func.__code__.co_argcount:
            raise ValueError(f"la funcion necesita {n} argumentos posicionales")
        def wrapper(x: Vector) -> Vector:
            return func(*x)
        return cls(wrapper, n, m)
