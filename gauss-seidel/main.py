from ..utils.titulo import *
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

#<==============================METODO=GAUSS-SIEDEL================================>

def get_dim_sistema_cuadrado(
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
    A: matriz nxn de coeficientes del sistema lineal
    b: vector de n componentes de coeficientes del sistema
    x0: aproximacion inicial del valor de la solucion del sistema
    w: valor del parametro de relajacion omega elemento de (0,2)
    regresa: solucion aproximada del sistema lineal Ax = b
    """

    _ = get_dim_sistema_cuadrado(A,b)

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

    n = get_dim_sistema_cuadrado(A,b)
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
        x0: np.ndarray
        dim: int
        inicializado: bool

    sistema = SistemaLineal(np.empty(0), np.empty(0), np.empty(0), 0, False)

    def print_sistema(coef, const, **kwargs) -> None:
        print(str_sistema_lineal(
            coef.tolist(),
            const.tolist(),
            lambda x: f"{x:5.2f}"[:5].center(5)
        ), **kwargs)

    def print_vector(v,**kwargs) -> None:
        vec_var = str_vector([f"x{i+1}" for i in range(sistema.dim)])
        vec_fmt = lambda v: str_vector(v, lambda x: f"{x:.2f}")
        print(vec_var + f" = {vec_fmt(v)}", **kwargs)


    def mensaje(sistema: SistemaLineal):
        print("Solucionador de sistemas lineales iterativo:",
              "***Metodo de Relajacion***", sep="\n"
        )
        if sistema.inicializado:
            
            print("\nConfiguracion del sistema:")
            print_sistema(sistema.coef, sistema.const, end="\n\n")
 
            print("Aproximacion Inicial:")
            print_vector(sistema.x0, end="\n\n")

            try:
                res = gauss_seidel(sistema.coef, sistema.const, sistema.x0)
                print("Solucion Aproximada:")
                print_vector(res, end="\n\n")
            except (RuntimeError, ZeroDivisionError):
                print("El sistema actual no puede ser resuelto "
                      "directamente por gauss-seidel", end="\n\n")


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def cargar_sistema(sistema: SistemaLineal):
        print(
            "Introduzca alguna de las siguientes instrucciones:",
            "'N'        : Generar un sistema de N ecuaciones",
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
                    "\nIngrese las ecuaciones:",
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
            for opcion in menu.opciones:
                opcion.activa = True
            sistema.inicializado = True

        print("\nEl sistema ha sido cargado exitosamente")


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def mostrar_proceso(sistema: SistemaLineal):
        tabla = Tabla(*[f"x{i}" for i in range(1,sistema.dim+1)])
        x = sistema.x0.copy()
        it = gauss_seidel_iter(sistema.coef, sistema.const, x)
        print("Tabla de iteraciones realizadas para el sistema:")
        print_sistema(sistema.coef, sistema.const, end="\n\n")
        print(tabla.encabezado())
        print(tabla.fila(*x))
        for _ in it: print(tabla.fila(*x))


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
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
                "\nIngrese la ecuacion:"
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
    

    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
    def modificar_constantes(estado: SistemaLineal):

        print(str_sistema_lineal(
            estado.coef.tolist(),
            estado.const.tolist()
        ))

        print(
            "Introduzca el vector de constantes",
            "con el siguente formato: b1 b2 ... bn",
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


    @Menu.esperar_entrada
    @Menu.limpiar_pantalla
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

    menu = Menu(sistema, [
            Opcion("Cargar Sistema", cargar_sistema),
            Opcion("Mostrar Proceso", mostrar_proceso, activa=False),
            Opcion("Modificar Ecuacion", modificar_ecuacion, activa=False),
            Opcion("Modificar Constantes", modificar_constantes, activa=False),
            Opcion("Modificar Valor Inicial", modificar_val_init, activa=False),
            Opcion("Salir", salir)
        ],
        pre=mensaje,
    )

    while True:
        menu.mostrar()
        menu.seleccionar()
