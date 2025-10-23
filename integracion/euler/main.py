from ...utils.equipo import *
from ...utils.ansi import *
from ...utils.menu import *
from ...utils.deps.np import *
from ...utils.deps.sympy import *

#<==============Implementacion del metodo de Euler para EDOs==================>

from typing import Callable, cast

def euler(
    f: Callable[[float, float], float],
    x0: float,
    y0: float,
    xf: float,
    h: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Resuelve una EDO de la forma dy/dx = f(x, y) con condicion inicial y(x0) = y0
    desde x0 hasta xf utilizando el metodo de Euler con tamaño de paso h.
    
    Retorna:
        (x_vals, y_vals): Arrays con los valores de x y y en cada paso
    """
    if h <= 0: raise ValueError(
        "el tamaño de paso h debe ser positivo"
    )
    if x0 == xf: return np.array([x0]), np.array([y0])
    
    n = int(abs((xf - x0) / h))

    h_ajustado = (xf - x0) / n if n > 0 else (xf - x0)
    
    x_vals = np.zeros(n + 1)
    y_vals = np.zeros(n + 1)
    
    x_vals[0] = x0
    y_vals[0] = y0
    
    for i in range(n):
        y_vals[i + 1] = y_vals[i] + h_ajustado * f(x_vals[i], y_vals[i])
        x_vals[i + 1] = x_vals[i] + h_ajustado
    
    return x_vals, y_vals

if __name__ == "__main__":

    from dataclasses import dataclass
    @dataclass
    class Estado:
        expr: sympy.Basic
        f: Callable[[float, float], float]
        h: float = 0.1

    def status(estado: Estado | None):
        if estado is None: return
        print(
            "Resolutor de EDOs: Metodo de Euler", 
            f"dy/dx = f(x, y) = {estado.expr}",
            f"h = {estado.h} (tamaño de paso)",
            sep="\n"
        ) 

    def introducir_funcion(estado: Estado | None):
        global menu
        x, y = sympy.symbols("x y")
        try:
            expr = sympy.sympify(input("f(x, y) = ").strip())
        except sympy.SympifyError as e:
            print(f"Expresion invalida:\n{e}")
            return

        if expr.free_symbols:
            if expr.free_symbols <= {x, y}:
                f = sympy.lambdify((x, y), expr, modules="numpy")
            else:
                print("Ej. de f(x,y): x + y, x**2 - y, etc.")
                print("Solo use las variables 'x' y 'y'")
                input()
                return
        else:
            try:
                val = float(cast(float, expr))
                f = lambda x_val, y_val: val
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
    def resolver_edo(estado: Estado):
        try:
            x0 = float(input("x0 = "))
            y0 = float(input("y0 = "))
            xf = float(input("xf = "))
        except ValueError:
            print("Introduzca un numero!")
            return 
        
        x_vals, y_vals = euler(estado.f, x0, y0, xf, estado.h)
        
        print(f"\nSolucion de dy/dx = {estado.expr}")
        print(f"Condicion inicial: y({x0}) = {y0}")
        print(f"Tamaño de paso: h = {estado.h}")
        print(f"Resultado: y({xf}) ≈ {y_vals[-1]:.6f}")
        print(f"\nPrimeros y ultimos valores:")
        print(f"x={x_vals[0]:.4f}, y={y_vals[0]:.6f}")
        if len(x_vals) > 1:
            print(f"x={x_vals[1]:.4f}, y={y_vals[1]:.6f}")
        if len(x_vals) > 2:
            print("...")
            print(f"x={x_vals[-2]:.4f}, y={y_vals[-2]:.6f}")
        print(f"x={x_vals[-1]:.4f}, y={y_vals[-1]:.6f}")

    @Opcion.requerir_estado
    def modificar_pasos(estado: Estado): 
        try:
            h = float(input("h = "))
        except ValueError:
            print("Introduzca un numero")
            input()
            return
        if h <= 0:
            print("Introduzca un numero positivo")
            input()
            return
        estado.h = h

    def salir(_):
        altscreen(False)
        exit()

    menu = Menu([
        Opcion("Introducir Funcion", introducir_funcion),
        Opcion("Resolver EDO", resolver_edo, activa = False),
        Opcion("Modificar Tamaño de Paso (h)", modificar_pasos, activa=False), 
        Opcion("Salir", salir)],
        pre = status
    )

    altscreen(True)
    while True: menu.desplegar()
