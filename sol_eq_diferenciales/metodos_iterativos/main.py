from ...utils.equipo import *
from ...utils.ansi import *
from ...utils.menu import *
from ...utils.tabla import *
from ...utils.deps.np import *
from ...utils.deps.sympy import *
from ...utils.grafica import *

#<==============Implementacion del metodo de Euler para EDOs==================>

import math
from typing import Callable, NamedTuple, cast
from functools import partial
import sympy
import numpy as np

Funcion = Callable[[float, float], float]

class Punto(NamedTuple):
    x: float
    y: float

def euler(dydx: Funcion, p: Punto, h: float) -> Punto:
    return Punto(
        p.x + h,
        p.y + dydx(p.x, p.y)*h
    )

def heun(dydx: Funcion, p: Punto, h: float) -> Punto:
    y = p.y + dydx(p.x, p.y)*h
    return Punto(
        p.x + h,
        p.y + (dydx(p.x, p.y)+dydx(p.x+h, y))*h/2
    )

def punto_medio(dydx: Funcion, p: Punto, h: float) -> Punto:
    y = p.y + dydx(p.x,p.y)*h/2
    return Punto(
        p.x + h,
        p.y + dydx(p.x+h/2, y)*h
    )

def runge_kutta_orden_2(dydx: Funcion, p: Punto, h: float) -> Punto:
    k1 = dydx(p.x, p.y)
    k2 = dydx(p.x+0.75*h, p.y+0.75*k1*h)
    return Punto(
        p.x + h,
        p.y + (k1/3 + 2*k2/3)*h
    )

def runge_kutta_orden_3(dydx: Funcion, p: Punto, h: float) -> Punto:
    k1 = dydx(p.x, p.y)
    k2 = dydx(p.x+0.5*h, p.y+0.5*k1*h)
    k3 = dydx(p.x+h, p.y-k1*h-2*k2*h)
    return Punto(
        p.x + h,
        p.y + (k1+4*k2+k3)*h/6
    )

def runge_kutta_orden_4(dydx: Funcion, p: Punto, h: float) -> Punto:
    k1 = dydx(p.x, p.y)
    k2 = dydx(p.x+0.5*h, p.y+0.5*k1*h)
    k3 = dydx(p.x+0.5*h, p.y+0.5*k2*h)
    k4 = dydx(p.x+h, p.y+k3*h)
    return Punto(
        p.x + h,
        p.y + (k1+2*k2+2*k3+k4)*h/6
    )

Metodo = Callable[[Funcion, Punto, float], Punto]

def titulo_metodo(metodo: Metodo) -> str:
    return " ".join(
        palabra.capitalize() for palabra
        in metodo.__name__.split("_")
    )

def aproximar_intervalo_eq_dif(
        metodo: Metodo,
        dydx: Funcion,
        xf: float,
        p: Punto,
        h: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Regresa el conjunto de puntos que aproximan la EDO de primer grado con la
    forma dy/dx = f(x,y) desde p.x hasta xf con la condicion inicial que p es
    un punto valido de la solucion.
    """
    
    assert h != 0
    if h < 0: assert xf <= p.x
    if h > 0: assert xf >= p.x

    r, n = math.modf((xf-p.x)/ h)
    n = int(n)
    arr_len = n if np.isclose(r, 0) else n+1
    X = np.empty(arr_len)
    Y = np.empty(arr_len)
    
    for i in range(n):
        p = metodo(dydx, p, h)
        X[i] = p.x
        Y[i] = p.y
    if arr_len != n:
        p = metodo(dydx, p, h*r)
        X[-1] = p.x
        Y[-1] = p.y

    return X, Y


def solucionar_edo(
    metodo: Metodo,
    dydx: Funcion,
    a: float,
    b: float,
    p: Punto,
    h: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Regresa el conjunto de puntos que aproximan la EDO de primer grado con la forma
    dy/dx = f(x, y) desde x=a hasta x=b dada la condicion la condicion inicial que
    la sol. pasa por el punto p utilizando el metodo proporcionado con tamaño de paso h.
    
    Retorna:
        (x_vals, y_vals): Arrays con los valores de x y y en cada paso
    """
   
    assert h > 0
    if a > b: a, b = b, a

    if p.x < a:
        while p.x < a-h:
            p = metodo(dydx, p, h)
        p = metodo(dydx, p, a-p.x)
    if p.x > b:
        while p.x > b+h:
            p = metodo(dydx, p, -h)
        p = metodo(dydx, p, b-p.x)

    X_izq, Y_izq = aproximar_intervalo_eq_dif(metodo, dydx, a, p, -h)
    X_der, Y_der = aproximar_intervalo_eq_dif(metodo, dydx, b, p, h)

    X = np.concatenate((np.flip(X_izq), np.atleast_1d(p.x), X_der))
    Y = np.concatenate((np.flip(Y_izq), np.atleast_1d(p.y), Y_der))

    return X, Y

if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class Estado:
        metodos: dict[Metodo, bool]
        expr: sympy.Expr
        f: Callable[[float, float], float]
        h: float = 0.1
        puntos: list[tuple[float, float]] | None = None

    def status(estado: Estado | None):
        if estado is None: return
        print(
            "Solucionador de Ecuaciones Diferenciales Ordinarias", 
            f"dy/dx = {estado.expr}",
            f"h = {estado.h} (tamaño de paso)",
            sep="\n"
        ) 

   
    def symbols() -> tuple[sympy.Symbol, sympy.Symbol]:
        return sympy.symbols("x y")

    def parsear(expr: str) -> sympy.Expr: 
        defs = {
            'x'  : sympy.symbols('x'),
            'y'  : sympy.symbols('y'),
            'e'  : sympy.E,
            'pi' : sympy.pi
        }
        return sympy.parse_expr(expr, local_dict=defs, transformations=
            sympy.parsing.sympy_parser.standard_transformations + (
            sympy.parsing.sympy_parser.convert_xor,
            sympy.parsing.sympy_parser.implicit_multiplication_application
        ))

    def lambdify(expr: sympy.Expr) -> Funcion:
        return sympy.lambdify(symbols(), expr, modules="numpy")


    def es_inicializador(
        generador_de_argumentos: Callable[[], tuple[sympy.Expr, Funcion] | None]
    ) -> Accion:
        def wrapper(estado: Estado | None):
            global menu
            args = generador_de_argumentos()
            if not args: return
            expr, f = args
            if estado:
                estado.expr = expr
                estado.f = f
            else:
                menu.estado = Estado(
                    {
                        euler       : True,
                        heun        : False,
                        punto_medio : False,
                        runge_kutta_orden_2: False,
                        runge_kutta_orden_3: False,
                        runge_kutta_orden_4: False
                    }, expr, f
                )
                for opcion in menu.opciones:
                    opcion.activa = True
        return wrapper


    def entrada_funcion() -> tuple[sympy.Expr, Funcion] | None:
        try:
            expr = parsear(input("f(x,y) = ").strip())
        except sympy.SympifyError as e:
            print(f"Expresion invalida:\n{e}")
            return

        x, y = symbols()
        if expr.free_symbols:
            if expr.free_symbols <= {x, y}:
                f = lambdify(expr)
            else:
                print("Ej. de f(x,y): x + y, x**2 - y, etc.")
                print("Solo use las variables 'x' y 'y'")
                input()
                return
        else:
            try:
                val = float(cast(float, expr))
                f = lambda *_: val
            except (ValueError, TypeError):
                print("La expresion constante debe ser un numero valido.")
                return

        return expr, f

    introducir_derivada = es_inicializador(entrada_funcion)


    @Opcion.requerir_estado
    def resolver_edo(estado: Estado):
        print( f"Ecuacion diferencial : dy/dx = {estado.expr}")
        print( f"Tamaño de paso       : h = {estado.h}")
        try:
            a = float(input(
                "Inicio del intervalo : a = "))
            b = float(input(
                "Fin del intervalo    : b = "))
            token = input(
                "Codicion Inicial     : x,y = ")
            x, y = (float(val) for val in token.split(","))
        except ValueError:
            print("Introduzca valores numericos!")
            return 
     
        tabla = Tabla("x", "y")

        metodos_activos = [
            m for m, activo in estado.metodos.items() if activo
        ]
        for metodo in metodos_activos:
            X, Y = solucionar_edo(
                metodo, estado.f, a, b, Punto(x,y), estado.h
            )
            print(
                "",
                "Metodo de " + titulo_metodo(metodo),
                tabla.encabezado(), sep="\n"
            )
            for xi, yi in zip(X,Y): print(tabla.fila(xi,yi))
            input()

    @Opcion.requerir_estado
    def modificar_paso(estado: Estado): 
        try:
            h = float(input("h = "))
        except ValueError:
            print("Introduzca un numero")
            input()
            return
        if h <= 0:
            print("La distancia de paso debe ser positiva")
            input()
            return
        estado.h = h


    @Opcion.requerir_estado
    def modificar_metodos(estado: Estado):

        continuar = True
        def regresar():
            nonlocal continuar
            continuar = False

        def alternar_metodo(metodos: dict[Metodo, bool], metodo: Metodo, *_):
            if metodos[metodo]: metodos[metodo] = False
            else: metodos[metodo] = True

        opciones = [
            Opcion("", partial(alternar_metodo, estado.metodos, metodo))
            for metodo in estado.metodos
        ]
        opciones.append(Opcion("Regresar", lambda _: regresar()))
        sub = Menu(opciones)

        while continuar:
            for opcion, metodo, activo in zip(
            sub.opciones, estado.metodos, estado.metodos.values()):
                opcion.nombre = " ".join([
                    "Desactivar" if activo else "Activar",
                    "Metodo de", titulo_metodo(metodo)
                ])
            sub.desplegar()


    @Opcion.requerir_estado
    def cargar_grafica(estado: Estado):
        try:
            a = float(input(
                "Inicio del intervalo : a = "))
            b = float(input(
                "Fin del intervalo    : b = "))
            token = input(
                "Codicion Inicial     : x,y = ")
            x, y = (float(val) for val in token.split(","))
            p0 = Punto(x,y)
        except ValueError:
            print("Introduzca valores numericos!")
            return

        resultados = {}
        for metodo in estado.metodos.keys():
            X, Y = solucionar_edo(metodo, estado.f, a, b, p0, estado.h)
            resultados[metodo] = (X, Y)
        if not resultados:
            print("No hubo resultados validos para graficar")
            input("Presione enter para continuar")
            return


        y_vals = np.concatenate([Y for _, Y in resultados.values()])
        y_min, y_max = np.min(y_vals), np.max(y_vals)
        margen_y = (y_max - y_min) * 0.1
        vista = Vista(a, b, y_min - margen_y, y_max + margen_y)

        print("\nMostrando gráfica con métodos y solución analítica...")
        print("Cierre la gráfica para continuar.")
        grafica = Grafica(vista)

        for metodo, (X, Y) in resultados.items():
            nombre_legible = titulo_metodo(metodo) 
            grafica.curva(f"Método: {nombre_legible}", X, Y, linestyle="--", marker=".", label=f"Método de {nombre_legible}")

        X_analitico = []
        Y_analitico = []

        try:
            x_sym, y_sym = sympy.symbols('x y')
            y_func = sympy.Function('y')
            expr = sympy.sympify(estado.expr) if isinstance(estado.expr, str) else estado.expr

            solution = sympy.dsolve(
                y_func(x_sym).diff(x_sym) - expr.subs({y_sym: y_func(x_sym)}),
                y_func(x_sym),
                ics={y_func(p0.x): p0.y}
            )

            if isinstance(solution, list):
                solution = solution[0]

            if isinstance(solution, sympy.Equality):
                sol_lambda = sympy.lambdify(x_sym, solution.rhs, 'numpy')
                X_analitico = np.linspace(a, b, 200)
                Y_analitico = np.real(sol_lambda(X_analitico))
                grafica.curva(
                    "Solucion real",
                    X_analitico.tolist(),
                    Y_analitico.tolist(),
                    color="black",
                    linewidth=2,
                    label="Solucion real"
                )
            else:
                print("No se pudo encontrar una solución analítica procesable.")

        except Exception as e:
            print(f"Advertencia: No se pudo calcular la solución analítica: {e}")

        grafica._ax.legend()
        grafica.mostrar()


    @es_inicializador
    def cargar_ejemplo() -> tuple[sympy.Expr, Funcion] | None:
        ejs = [
            "-2x^3 + 12x^2 - 20x + 8.5",
            "4exp(0.8x) - 0.5y",
            "x + y",
        ]

        exprs = [parsear(ej) for ej in ejs] 
        funcs = [lambdify(expr) for expr in exprs]

        expr_final = None
        f_final = None

        def cargar_valores(expr: sympy.Expr, f: Funcion, *_):
            nonlocal expr_final, f_final
            expr_final = expr
            f_final = f

            
        opciones = [
            Opcion(f"{ej}", partial(cargar_valores, expr, f))
            for ej, expr, f in zip(ejs, exprs, funcs)
        ]
        opciones.append(Opcion("Cancelar", lambda _: None))
        Menu(opciones).desplegar()

        if expr_final is None or f_final is None: return
        return expr_final, f_final


    def salir(_): exit()


    menu = Menu([
        Opcion("Introducir Derivada", introducir_derivada),
        Opcion("Resolver EDO", resolver_edo, activa = False),
        Opcion("Modificar Tamaño de Paso", modificar_paso, activa=False),
        Opcion("Modificar Metodos", modificar_metodos, activa=False),
        Opcion("Cargar graficas", cargar_grafica, activa=False),
        Opcion("Cargar Ejemplo", cargar_ejemplo),
        Opcion("Salir", salir)],
        pre = status
    )

    while True: menu.desplegar()
