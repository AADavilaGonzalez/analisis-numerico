from ..utils.equipo import *
from ..utils.deps.np import *
from ..utils.menu import *
from ..utils.grafica import *

import math
from typing import Callable
from functools import lru_cache

# <=========IMPLEMENTACION DE ALGORITMO DE DIFERENCIAS DIVIDIDAS============>

def diferencias_divididas(
    X: np.ndarray,
    Y: np.ndarray,
) -> Callable[[float], float]:
   
    if X.ndim != 1 or Y.ndim != 1:
        raise ValueError("X,Y deben ser vectores")

    if X.shape[0] != Y.shape[0]:
        raise ValueError("X,Y deben ser del mismo tamano")

    n = X.shape[0]
    if not n:
        raise ValueError("Se necesita al menos un punto")
    if n == 1:
        return lambda _: Y[0] 
   
    #j > i ; i,j en N
    @lru_cache
    def dif(i: int , j:int) -> float:
        if j - i == 1:
            return (Y[j]-Y[i])/(X[j]-X[i])
        return (dif(i+1,j)-dif(i,j-1))/(X[j]-X[i])
    
    coef = [dif(0,i) for i in range(1, n)]

    def f(x: float) -> float:
        y = Y[0]
        for i in range(1,n):
            y += coef[i-1]*math.prod(x-X[j] for j in range(i))
        return y
   
    return f

if __name__ == "__main__":

    from dataclasses import dataclass
    @dataclass
    class Estado:
        X: np.ndarray
        Y: np.ndarray
        f: Callable[[float], float]
        vista: Vista
        inicializado: bool = False
        corriendo: bool = True
    
    estado = Estado(
        X = np.zeros(0),
        Y = np.zeros(0),
        f = lambda _: math.nan,
        vista = Vista(
            math.nan,
            math.nan,
            math.nan,
            math.nan
        )
    )

    MARGEN = 0.1

    def ingresar_datos(estado: Estado):
        print("Ingrese los puntos para generar la aproximacion polinomial",
              "Utilice el siguiente formato: x,y | ej. 1,-2",
              "Ingrese una linea vacia para terminar la captura", sep="\n")
        X: list[float] = []
        Y: list[float] = []
        
        while True:
            token = input("> ")
            if not token:
                break
            try:
                x, y = tuple(map(float, token.split(",",1)))
            except ValueError:
                print("Formato Incorrecto!")
                continue
            X.append(x)
            Y.append(y)
        
        if len(X) == 0: return

        estado.X = np.array(X)
        estado.Y = np.array(Y)

        x_min = min(X)
        x_max = max(X)
        x_margen = (x_max-x_min)*MARGEN
       
        y_min = min(Y)
        y_max = max(Y)
        y_margen = (y_max-y_min)*MARGEN

        estado.vista = Vista(
            x_min-x_margen,
            x_max+x_margen,
            y_min-y_margen,
            y_max+y_margen
        )
        estado.f = diferencias_divididas(estado.X, estado.Y)

        if not estado.inicializado:
            global menu
            for opcion in menu.opciones: opcion.activa=True
            estado.inicializado = True


    def graficar_aproximacion(estado: Estado):
        print("Desplegando Grafica de la Aproximacion Calculada",
              "Cierre la grafica para continuar...", sep="\n")
        grafica = Grafica(estado.vista)
        margen = (estado.vista.x_max-estado.vista.x_min)*(MARGEN+0.05)
        grafica.funcion("", estado.f,
            estado.vista.x_min-margen,
            estado.vista.x_max+margen,
        )
        for x,y in zip(estado.X, estado.Y):
            grafica.punto("", x, y, color="blue")
        grafica.mostrar()

    @Menu.esperar_entrada
    def evaluar_aproximacion(estado: Estado):
        print("Valor de x a evaluar:")
        try:
            x = float(input("> "))
        except:
            print("Formato Incorrecto!")
            return
        print(f"f(x) = {estado.f(x)}")

 
    def salir(estado: Estado): estado.corriendo = False 
   
    def imprimir_menu_principal(estado: Estado):
        print("Aproximador de Funciones Mediante Metodo de Diferencias Finitas")
        if estado.inicializado:
            print(f"Datos: [{", ".join(
                f"({x},{y})" for x,y in zip(estado.X, estado.Y)
            )}]")

    menu = Menu(estado, [
            Opcion("Ingresar Conjunto de Datos", ingresar_datos),
            Opcion("Graficar Aproximacion", graficar_aproximacion, activa=False),
            Opcion("Evaluar Aproximacion", evaluar_aproximacion, activa=False),
            Opcion("Salir", salir)
        ],
        pre=imprimir_menu_principal
    )

    menu.desplegar_mientras(lambda estado: estado.corriendo)

