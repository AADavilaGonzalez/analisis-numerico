from ...utils.titulo import *
from ...utils.ansi import *
from ...utils.menu import *
from ...utils.rutinas import *

try:
    import numpy as np
except ImportError:
    print("El paquete numpy es obligatorio para correr este programa",
              "por favor instale el paquete utilizando el siguiente comando",
              "[py/python/python3] -m pip install numpy", sep="\n")
    exit()

#<==============================METODO=DE=JACOBI================================>

def metodo_jacobi(
    A: np.ndarray,
    b: np.ndarray, 
    x0: np.ndarray | None,
    err: float  = 0.001,
    max_iter: int = 10000,
    freq_chequeo: int = 10 
) -> np.ndarray:
    """
    Metodo de Jacobi iterativo para resolver sistemas de ecuaciones lineales
    A: matriz nxn de coeficientes del sistema lineal
    b: vector de n componentes de coeficientes del sistema
    x0: aproximacion inicial del valor de la solucion del sistema
    regresa: solucion aproximada del sistema lineal Ax = b
    """
    
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A debe ser una matriz cuadrada")

    n = A.shape[0]
    if b.ndim != 1 or b.shape[0] != n:
        raise ValueError("b debe ser un vector compatible con A")

    D_inv = 1.0 / np.diag(A) 
    R = A.copy()
    np.fill_diagonal(R, 0)

    x = np.zeros(n) if x0 is None else x0.copy()

    err_prev = float("inf")

    for i in range(1,max_iter+1):
        x = D_inv*(b - R@x)
        #error por componente maximo del residual
        err_act = np.linalg.norm(b-A@x, ord=np.inf)
        if i % freq_chequeo == 0:
            if err_act >= err_prev: raise RuntimeError(
                "el metodo diverge bajo las condicione dadas:"
                f"(error: {err_prev}, iteracion: {i})")
            err_prev = err_act
        if err_act <= err:
            return x

    return x


if __name__ == "__main__":
   
    from dataclasses import dataclass
    @dataclass
    class SistemaLineal:
        coef: np.ndarray
        const: np.ndarray
        x0: np.ndarray
        dim: int
        inicializado: bool

    sistema = SistemaLineal(np.empty(0), np.empty(0), np.empty(0), 0, False)

    @Opcion.requerir_estado
    def mensaje(sistema: SistemaLineal):
        print("Solucionador de sistemas lineales iterativo: Metodo de Jacobi")
        if sistema.inicializado:
            
            print("\nConfiguracion del sistema:",)
            print(str_sistema_lineal(
                sistema.coef.tolist(),
                sistema.const.tolist(),
                lambda x: f"{x:5.2f}"[:5].center(5)
            ), end = "\n\n")

            vec_var = str_vector([f"x{i+1}" for i in range(sistema.dim)])
            vec_fmt = lambda v: str_vector(v, lambda x: f"{x:.2f}")
    
            print("Aproximacion inicial:")
            print(vec_var + f" = {vec_fmt(sistema.x0)}", end="\n\n")

            try:
                res = metodo_jacobi(sistema.coef, sistema.const, sistema.x0)
                print("Solucion Aproximada:")
                print(vec_var + f" = {vec_fmt(res)}", end="\n\n")
            except (RuntimeError, ZeroDivisionError):
                print("El sistema actual no puede ser resuelto"
                        " directamente por el metodo de Jacobi", end="\n\n")


    @Opcion.esperar_entrada
    @Opcion.limpiar_pantalla
    @Opcion.requerir_estado
    def cargar_sistema(sistema: SistemaLineal):
        print(
            "Introduzca alguna de las siguientes instrucciones:",
            "'N' : Generar un sistema de N ecuaciones",
            "'RANDOM N' : Generar un sistema de N ecuaciones aleatorias",
            "Donde N es un numero natural",
            sep="\n"
        )

        tokens = input("> ").split()
        try:
            if tokens[0] == "RANDOM":
                n = int(tokens[1])
                sistema.coef, sistema.const = (
                    np.array(arr) for arr in
                    generar_sistema_lineal(n)
                )
                sistema.coef += 15*np.eye(n)
            else:
                n = int(tokens[0])
                print(
                    "Ingrese las ecuaciones:",
                    "a1*x1 + a2*x2 + ... + an*xn = b",
                    "con el siguiente formato:",
                    "a1 a2 ... an b",
                    sep = "\n"
                )
                sistema.coef, sistema.const = (
                    np.array(arr) for arr in leer_sistema_lineal(n)
                )
            sistema.dim = n
        except Exception:
            print("formato incorrecto")
            return

        sistema.x0 = np.zeros(sistema.dim) 

        if not sistema.inicializado:
            global menu
            menu.opciones[1].activa = True
            menu.opciones[2].activa = True
            menu.opciones[3].activa = True
            sistema.inicializado = True

        print("\nEl sistema ha sido cargado exitosamente")


    @Opcion.esperar_entrada
    @Opcion.limpiar_pantalla
    @Opcion.requerir_estado
    def modificar_ecuacion(sistema: SistemaLineal):

        print("Introduzca el indice de la ecuacion que desea modificar")
        print(str_sistema_lineal(
            sistema.coef.tolist(),
            sistema.const.tolist(),
            indices = True
        ))

        try:
            i = int(input("> ")) - 1
            if i not in range(sistema.dim):
                raise ValueError()
        except Exception:
            print("opcion invalida")
            return

        print(
                "Ingrese la ecuacion:"
                "a1*x1 + a2*x2 + ... + an*xn = b",
                "con el siguiente formato:",
                "a1 a2 ... an b",
                sep="\n"
        )
        try:
            vals = leer_vector(sistema.dim+1)
        except ValueError:
            print("formato incorrecto")
            return
        
        for j in range(sistema.dim):
            sistema.coef[i,j] = vals[j]
        sistema.const[i] = vals[sistema.dim]

        print(f"\nEcuacion {i+1} modificada exitosamente")
    

    @Opcion.esperar_entrada
    @Opcion.limpiar_pantalla
    @Opcion.requerir_estado
    def modificar_constantes(estado: SistemaLineal):

        print(str_sistema_lineal(
            estado.coef.tolist(),
            estado.const.tolist()
        ))

        print(
            "Introduzca el vector de constantes",
            "<b1, b2, ..., bn> con el siguente formato:",
            "b1 b2 ... bn",
            sep="\n"
        )

        try:
            vals = leer_vector(estado.dim)
        except ValueError:
            print("formato incorrecto")
            return

        for i in range(estado.dim):
            estado.const[i] = vals[i]
        print("\nConstantes del sistema modificados exitosamente")


    @Opcion.esperar_entrada
    @Opcion.limpiar_pantalla
    @Opcion.requerir_estado
    def modificar_val_init(estado: SistemaLineal):

        print("Valor Inicial: " + str_vector(estado.x0.tolist()))

        print(
            "Introduzca el vector de valor incial",
            "con el siguente formato: b1 b2 ... bn",
            sep="\n"
        )

        try:
            vals = leer_vector(estado.dim)
        except ValueError:
            print("formato incorrecto")
            return

        for i in range(estado.dim):
            estado.x0[i] = vals[i]
        print("\nValor inicial modificado exitosamente")


    def salir(*_) -> None:
        clear()
        exit()

    menu = Menu([
            Opcion("Cargar Sistema", cargar_sistema),
            Opcion("Modificar Ecuacion", modificar_ecuacion, activa=False),
            Opcion("Modificar Constantes", modificar_constantes, activa=False),
            Opcion("Modificar Punto Inicial", modificar_val_init, activa=False),
            Opcion("Salir", salir)
        ],
        estado = sistema,
        pre=mensaje
    )

    while True:
        clear() 
        menu.mostrar()
        menu.seleccionar()
