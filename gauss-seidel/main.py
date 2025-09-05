from ..utils.equipo import *
from ..utils.menu import *
from ..utils.tabla import *
from ..utils.rutinas import *

try:
    import numpy as np
except ImportError:
    print("El paquete numpy es obligatorio para correr este programa",
            "por favor instale el paquete utilizando el siguiente comando",
            "[py/python/python3] -m pip install numpy", sep="\n")
    exit()

from typing import Iterator

#<==============================METODO=GAUSS-SIEDEL================================>

def get_dim_estado_cuadrado(
    A: np.ndarray,
    b: np.ndarray,
) -> int:
    if A.ndim != 2 or A.shape[0] != A.shape[0]:
        raise ValueError("A no es una matriz cuadrada")

    n = A.shape[0]
    if b.ndim != 1 or b.shape[0] != n:
        raise ValueError("b no es un vector compatible con A")

    return n


def gauss_seidel_iter(
    A: np.ndarray,
    b: np.ndarray, 
    x: np.ndarray,
    w: float = 1,
    err: float  = 0.000001,
    max_iter: int = 10000,
    freq_chequeo: int = 10 
) -> Iterator[None]:
    """
    Solucionador lineal por metodo de gauss-seidel con parametro
    de relajacion tambien conocido como metodo SOR
    A: matriz nxn de coeficientes del estado lineal
    b: vector de n componentes de coeficientes del estado
    x0: aproximacion inicial del valor de la solucion del estado
    w: valor del parametro de relajacion omega elemento de (0,2)
    regresa: solucion aproximada del estado lineal Ax = b
    """

    _ = get_dim_estado_cuadrado(A,b)

    if not 0 < w < 2:
        raise ValueError("valor de w fuera de rango")

    if any(x == 0 for x in A.diagonal()):
        raise ValueError("algun elemento de la diagonal principal es 0")
 
    L = np.tril(A, k=-1)
    D = np.diag(np.diag(A))
    U = np.triu(A, k=1)
    
    M = D + w*L
    c = w*b
    T = (1-w)*D - w*U

    del L, D, U

    err_prev = float("inf")

    for i in range(1,max_iter+1):
        #Actualizar la variable sin cambiar la referencia
        x[:] = np.linalg.solve(M, c+T@x)
        yield
        #error por componente maximo del residual
        err_act = np.linalg.norm(b-A@x, ord=np.inf)
        if freq_chequeo > 0 and i % freq_chequeo == 0:
            if err_act >= err_prev: raise RuntimeError(
                "el metodo diverge bajo las condicione dadas: "
                f"(error: {err}, iteracion: {i})")
            err_prev = err_act
        if err_act <= err:
            return


def gauss_seidel(
    A: np.ndarray,
    b: np.ndarray, 
    x0: np.ndarray | None,
    w: float = 1,
    err: float  = 0.000001,
    max_iter: int = 10000,
    freq_chequeo: int = 10 
) -> np.ndarray:

    n = get_dim_estado_cuadrado(A,b)
    x = np.zeros(n) if x0 is None else x0.copy()
    it = gauss_seidel_iter(A, b, x, w, err, max_iter, freq_chequeo)
    for _ in it: pass
    return x


if __name__ == "__main__":
   
    from dataclasses import dataclass

    @dataclass
    class SistemaLineal:
        coef: np.ndarray
        const: np.ndarray
        dim: int

    @dataclass
    class Estado:
        sistema: SistemaLineal
        x0: np.ndarray
        w: float
        inicializado: bool
        corriendo: bool

    estado = Estado(
        sistema = SistemaLineal(
            coef  = np.empty(0),
            const = np.empty(0),
            dim   = -1
        ),
        x0 = np.empty(0),
        w  = 1,
        inicializado = False,
        corriendo = True
    )


    def es_inicializador(f: Accion[Estado]) -> Accion[Estado]:
        def wrapper(estado: Estado):
            f(estado)
            if not estado.inicializado:
                global menu
                for opcion in menu.opciones:
                    opcion.activa = True
                estado.inicializado = True
        return wrapper


    def print_sistema(sistema: SistemaLineal, **kwargs) -> None:
        print(str_sistema_lineal(
            sistema.coef.tolist(),
            sistema.const.tolist(),
            lambda x: f"{x:5.2f}"[:5].center(5)
        ), **kwargs)


    def print_vector(v,**kwargs) -> None:
        vec_var = str_vector([f"x{i+1}" for i in range(estado.sistema.dim)])
        vec_fmt = lambda v: str_vector(v, lambda x: f"{x:.2f}")
        print(vec_var + f" = {vec_fmt(v)}", **kwargs)


    @Menu.esperar_entrada
    @es_inicializador
    def cargar_gauss_seidel(estado: Estado):
        estado.sistema.coef = np.array([
            [5, -3, 1],
            [2, 4, -1],
            [2, -3, 8],
        ], dtype=float)
        estado.sistema.const = np.array(
            [5, 6, 4], dtype=float
        )
        estado.sistema.dim = 3
        estado.x0 = np.array(
            [1,1,1], dtype=float
        )
        estado.w = 1
        print("\nGauss-Seidel cargado exitosamente")

    
    @Menu.esperar_entrada
    @es_inicializador
    def cargar_relajacion(estado: Estado):
        cargar_gauss_seidel(estado)
        estado.w = 1.1
        print("\nGauss-Seidel con relajacion cargado exitosamente")

   
    menu_ejemplos = Menu(estado, [
           Opcion("Gauss-Seidel", cargar_gauss_seidel),
           Opcion("Gauss-Seidel con Relajacion", cargar_relajacion),
           Opcion("Cancelar", lambda _: None)
        ],
        pre=lambda _: print("Elija el ejemplo de clase a cargar:\n"), 
    )


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def modificar_ecuacion(estado: Estado):

        print("Introduzca el indice de la ecuacion que desea modificar")
        print(str_sistema_lineal(
            estado.sistema.coef.tolist(),
            estado.sistema.const.tolist(),
            indices = True
        ))

        try:
            i = int(input("> ")) - 1
            if i not in range(estado.sistema.dim):
                raise ValueError()
        except Exception:
            print("opcion invalida")
            return

        print(
                "\nIngrese la ecuacion:"
                "a1*x1 + a2*x2 + ... + an*xn = b",
                "con el siguiente formato:",
                "a1 a2 ... an b",
                sep="\n"
        )
        try:
            vals = leer_vector(estado.sistema.dim+1)
        except ValueError:
            print("formato incorrecto")
            return
        
        for j in range(estado.sistema.dim):
            estado.sistema.coef[i,j] = vals[j]
        estado.sistema.const[i] = vals[estado.sistema.dim]

        print(f"\nEcuacion {i+1} modificada exitosamente")
    

    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def modificar_constantes(estado: Estado):

        print_sistema(estado.sistema)
        print(
            "Introduzca el vector de constantes",
            "con el siguente formato: b1 b2 ... bn",
            sep="\n"
        )

        try:
            vals = leer_vector(estado.sistema.dim)
        except ValueError:
            print("formato incorrecto")
            return

        for i in range(estado.sistema.dim):
            estado.sistema.const[i] = vals[i]
        print("\nConstantes del estado modificados exitosamente")


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def modificar_val_init(estado: Estado):

        print("Valor Inicial: " + str_vector(estado.x0.tolist()))

        print(
            "Introduzca el vector de valor incial",
            "con el siguente formato: b1 b2 ... bn",
            sep="\n"
        )

        try:
            vals = leer_vector(estado.sistema.dim)
        except ValueError:
            print("formato incorrecto")
            return

        for i in range(estado.sistema.dim):
            estado.x0[i] = vals[i]
        print("\nValor inicial modificado exitosamente")


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def modificar_w(estado: Estado):
        print(f"Parametro de Relajacion: {estado.w:.2f}")
        
        print("Introduzca el nuevo valor del parametro de relajacion",
              "como un un numero decimal en el intervalo (0,2):",
              sep="\n"
        )
        
        try:
            estado.w = float(input("> "))
        except ValueError:
            print("formato incorrecto")
            return

        print("Parametro de relajacion modificado exitosamente")


    menu_modificacion = Menu(estado, [
            Opcion("Modificar Ecuacion", modificar_ecuacion),
            Opcion("Modificar Constantes", modificar_constantes),
            Opcion("Modificar Valor Inicial", modificar_val_init),
            Opcion("Modificar Parametro 'w'", modificar_w)
        ],
        pre=lambda _: print("Elija el aspecto que desea modificar:\n"),
    )

    def mensaje(estado: Estado):
        print("Solucionador de estados lineales iterativo:",
              "***Metodo de Relajacion***", sep="\n"
        )
        if estado.inicializado:
            
            print("\nConfiguracion del estado:")
            print_sistema(estado.sistema, end="\n\n")
 
            print("Aproximacion Inicial:")
            print_vector(estado.x0, end="\n\n")

            print("Parametro de Relajacion:")
            print(f"w = {estado.w:.2f}", end="\n\n")

            try:
                res = gauss_seidel(
                    estado.sistema.coef,
                    estado.sistema.const,
                    estado.x0
                )
                print("Solucion Aproximada:")
                print_vector(res, end="\n\n")
            except (RuntimeError, ZeroDivisionError):
                #raise
                print("El estado actual no puede ser resuelto "
                      "directamente por gauss-seidel", end="\n\n")


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    @es_inicializador
    def cargar_sistema(estado: Estado):
        print(
            "Introduzca alguna de las siguientes instrucciones:",
            "'N'        : Generar un estado de N ecuaciones",
            "'RANDOM N' : Generar un estado de N ecuaciones aleatorias",
            "Donde N es un numero natural",
            sep="\n"
        )

        tokens = input("> ").split()
        try:
            if tokens[0] == "RANDOM":
                n = int(tokens[1])
                estado.sistema.coef, estado.sistema.const = (
                    np.array(arr) for arr in generar_sistema_lineal(n)
                )
                estado.sistema.coef += 15*np.eye(n)
            else:
                n = int(tokens[0])
                print(
                    "\nIngrese las ecuaciones:",
                    "a1*x1 + a2*x2 + ... + an*xn = b",
                    "con el siguiente formato una por linea:",
                    "a1 a2 ... an b",
                    sep = "\n"
                )
                estado.sistema.coef, estado.sistema.const = (
                    np.array(arr) for arr in leer_sistema_lineal(n)
                )
            estado.sistema.dim = n
        except Exception:
            print("formato incorrecto")
            return
       
        estado.x0  = np.zeros(estado.sistema.dim) 

        if not estado.inicializado:
            global menu
            for opcion in menu.opciones:
                opcion.activa = True
            estado.inicializado = True

        print("\nEl sistema ha sido cargado exitosamente")


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def mostrar_proceso(estado: Estado) -> None:
        tabla = Tabla(*[f"x{i}" for i in range(1,estado.sistema.dim+1)])
        x = estado.x0.copy()
        it = gauss_seidel_iter(estado.sistema.coef, estado.sistema.const, x)
        print("Tabla de iteraciones realizadas para el estado:")
        print_sistema(estado.sistema, end="\n\n")
        print(tabla.encabezado())
        print(tabla.fila(*x))
        try:
            for _ in it: print(tabla.fila(*x))
        except RuntimeError:
            print("Se detecto divergencia al solucionar el estado")


    def salir(estado: Estado): estado.corriendo = False

    menu = Menu(estado, [
            Opcion(
                "Cargar Sistema de Ecuaciones", 
                cargar_sistema
            ),
            Opcion(
                "Mostrar Proceso Iterativo",
                mostrar_proceso,
                activa=False
            ),
            Opcion(
                "Realizar Modificaciones", 
                lambda _: menu_modificacion.desplegar(),
                activa=False
            ),
            Opcion(
                "Cargar Ejemplos de Clase",
                lambda _: menu_ejemplos.desplegar(),
            ),
            Opcion("Salir", salir)
        ],
        pre=mensaje,
    )
    
    menu.desplegar_mientras(lambda estado: estado.corriendo == True)
