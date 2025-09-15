from ..utils.equipo import *
from ..utils.deps.np import *
from ..utils.menu import *
from ..utils.grafica import *

import math
from typing import Callable

# <=========IMPLEMENTACION DE INTERPOLACION DE LAGRANGE============>

class PolinomioLagrange:
    
    def __init__(self, X: np.ndarray, Y:np.ndarray):
        if X.ndim != 1 or Y.ndim != 1:
            raise ValueError("X,Y deben ser vectores")

        if X.shape[0] != Y.shape[0]:
            raise ValueError("X,Y deben ser del mismo tamano")

        self._n = X.shape[0]
        if not self.n:
            raise ValueError("Se necesita al menos un punto")

        self.X = X
        self.Y = Y

    @property
    def n(self) -> int:
        return self._n - 1

    def __call__(self, x: float) -> float:
        return sum(
            math.prod(
                (x-self.X[j])/(self.X[i]-self.X[j])
                for j in range(self._n)
                if j!=i
            ) * self.Y[i]
            for i in range(self._n)
        )
         

if __name__ == "__main__":

    from dataclasses import dataclass
    @dataclass
    class Estado:
        X: np.ndarray
        Y: np.ndarray
        f: Callable[[float], float]
        vista: Vista
        puntos: list[tuple]
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
        ), 
        puntos = []
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
        estado.f = PolinomioLagrange(estado.X, estado.Y)

        x_min = min(X)
        x_max = max(X)
        x_margen = (x_max-x_min)*MARGEN
       
        muestra_f = np.vectorize(estado.f)(np.linspace(x_min, x_max, 100))
        y_min = min(muestra_f)
        y_max = max(muestra_f)
        y_margen = (y_max-y_min)*MARGEN

        estado.vista = Vista(
            x_min-x_margen,
            x_max+x_margen,
            y_min-y_margen,
            y_max+y_margen
        )
        
        estado.puntos = []

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

        for x, y in estado.puntos:
            grafica.punto("", x, y, color="red")

        grafica.mostrar()

    @Menu.esperar_entrada
    def evaluar_aproximacion(estado: Estado):
        print("Valor de x a evaluar:")
        try:
            x = float(input("> "))
        except:
            print("Formato Incorrecto!")
            return
        estado.puntos.append((x,estado.f(x)))
        print(f"f(x) = {estado.f(x)}")

 
    def salir(estado: Estado): estado.corriendo = False 
   
    def imprimir_menu_principal(estado: Estado):
        print("Aproximador de Funciones Por Polynomios de Lagrange")
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

