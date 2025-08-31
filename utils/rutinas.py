from typing import TypeVar, Callable
from random import randint

T = TypeVar("T")

def leer_vector(
    n: int | None = None,
    tipo: Callable[[str], T] = float,
    prompt: str = "> "
) -> list[T]:
    
    v = [tipo(token) for token in input(prompt).split()] 
    if n and len(v) != n: raise ValueError(
        f"el vector debe tener un tamano de n={n}")
    return v
    

def leer_matriz(
    m: int, 
    n: int | None = None,
    tipo: Callable[[str], T] = float,
    prompt: str = "> "
) -> list[list[T]]:
    
    n = n or m
    return [leer_vector(n, tipo, prompt) for _ in range(m)]


def leer_sistema_lineal(
    n: int,
    tipo: Callable[[str], T] = float,
    prompt: str = "> "
) -> tuple[list[list[T]], list[T]]:
   
    if n < 1:
        raise ValueError("n debe ser mayor o igual a uno")

    coef = []
    const = []
    for _ in range(n):
        vals = leer_vector(n+1, tipo, prompt)
        coef.append(vals[0:n])
        const.append(vals[n])

    return coef, const


def generar_vector(
    n: int,
    generador: Callable[[int], T] = lambda *_: float(randint(-10,10))
) -> list[T]:

    return [generador(i) for i in range(n)]


def generar_matriz(
    m: int,
    n: int,
    generador: Callable[[int, int], T] = lambda *_: float(randint(-10,10))
) -> list[list[T]]: 

    return [generar_vector(n, lambda j: generador(i, j)) for i in range(m)]


def generar_sistema_lineal(
    n: int,
    generador_coef: Callable[[int, int], T] = lambda *_: float(randint(-10,10)),
    generador_const: Callable[[int], T] = lambda *_: float(randint(-10,10))
) -> tuple[list[list[T]], list[T]]:
    
    return generar_matriz(n, n, generador_coef), generar_vector(n, generador_const)


def str_vector(
    v: list[T],
    formato: Callable[[T], str] = lambda t: str(t),
    sangria: int = 0,
) -> str:

    return " " * sangria + f"< {", ".join(formato(x) for x in v)} >"

def str_matriz(
    mat: list[list[T]],
    formato: Callable[[T], str] = lambda t: str(t)[:5].center(5),
    sangria: int = 0
) -> str:

    return "\n".join(
        " " * sangria + f"| {" ".join(formato(x) for x in fila)} |"  
        for fila in mat
    )

def str_sistema_lineal(
    coef: list[list[T]],
    const: list[T],
    formato: Callable[[T], str] = lambda t: str(t),
    indices: bool = False,
    sangria: int = 0
) -> str:

    n = len(coef)
    if any(len(fila) != n for fila in coef):
        raise ValueError("la matriz coef debe ser cuadrada")

    if len(const) != n:
        raise ValueError("el vector const debe ser compatible con la matriz")

    lineas = []

    for i in range(n):
        linea = " " * sangria
        if indices:
            linea += f"{i+1}. "
        linea += " + ".join([
            f"{formato(coef[i][j])}*x{j+1}"
            for j in range(n)
        ]) + f" = {const[i]}"
        lineas.append(linea)

    return "\n".join(lineas)
