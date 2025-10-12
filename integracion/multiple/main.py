from ...utils.equipo import *
from ...utils.ansi import *
from ...utils.menu import *
from ...utils.deps.np import *
from ...utils.deps.sympy import *

import re
from typing import Callable


def integral_multiple_trapecio(
    f: Callable[..., np.ndarray],
    lims: list[tuple[float, float]],
    n: int
) -> float:

    if any(a == b for a,b in lims):
        return 0.0

    dims = len(lims)
    ejes = (np.linspace(a, b, n+1) for a,b in lims)
    #Broadcast para cambiar forma de los vectores
    ejes = [
        v.reshape((1,)*i + (len(v),) + (1,)*(dims-i-1))
        for i, v in enumerate(ejes)
    ]
    malla = f(*ejes)

    def regla_de_integracion(datos: np.ndarray, h: float) -> float:
        return h*(datos[1:-1].sum() + (datos[0]+datos[-1])/2)

    def integrar_malla(malla: np.ndarray, h: float) -> np.ndarray:
        nueva_malla = np.zeros(malla.shape[1:], dtype=float)
        for indice in np.ndindex(nueva_malla.shape):
            nueva_malla[indice] = regla_de_integracion(
                malla[(slice(None),) + indice], h
            )
        return nueva_malla

    for a,b in lims[:-1]:
        malla = integrar_malla(malla, (b-a)/n)

    a,b = lims[-1]
    return regla_de_integracion(malla, (b-a)/n) 


def integral_multiple_romberg(
    f : Callable[..., np.ndarray],
    lims : list[tuple[float, float]],
    k : int
) -> float:
    
    if any(a == b for a,b in lims):
        return 0.0
    
    R = np.zeros((k,k), dtype=float)
    
    for i in range(k):
        R[i, 0] = integral_multiple_trapecio(f, lims, 2**i)

    p = 1
    for j in range(1,k):
        p *= 4
        for i in range(j,k):
            R[i,j] = (p*R[i,j-1]-R[i-1,j-1])/(p-1)

    return R[k-1, k-1]
            
    
if __name__ == "__main__":

    regexEq = re.compile(r"^(.+)\((.+)\)\s*=\s*(.+)$")
    regexNom = re.compile(r"^[a-zA-Z]+$")
    regexVars = re.compile(r"^(?:\s*[a-zA-Z]\s*,)*(?:\s*[a-zA-Z]\s*)$")

    class Funcion:

        def __init__(self,
            nombre: str,
            vars: list[sympy.Symbol],
            expr: sympy.Expr 
        ):
            self._nombre = nombre
            self._vars = vars
            self._expr = expr

            self._f = sympy.lambdify(vars, expr, modules="numpy")

 
        def __call__(self, *args) -> np.ndarray:
            return self._f(*args)

        @property
        def nombre(self): return self._nombre

        @property
        def vars(self): return self._vars

        @property
        def expr(self): return self._expr

        def __str__(self):
            return f"{self.nombre}({",".join(v.name for v in self.vars)}) = {str(self.expr)}"


    class Estado:

        def __init__(self, f: Funcion):
            self.f: Funcion = f
            self.n: int = 10
            self.pres: int = 5
            self.metodo: Callable = integral_multiple_trapecio
            self.simbolo_arg: str = 'n'
            self.nombre_arg: str = "segmentos"
            self.nombre_metodo: str = "Regla del Trapecio"


    def introducir_funcion(estado: Estado | None):
        print("Introduzca una funcion")
        
        expr = input("> ").strip()
        m = regexEq.match(expr)
        if not m:
            print(
                "introduzca la funcion con el siguiente formato:",
                "<nombre de la funcion>(x, y, ...) = expresion",
                sep='\n'
            )
            input()
            return
        
        nombre, vars, expr = m.groups()
        if not regexNom.match(nombre):
            print("El nombre de la funcion solo puede contener letras")
            input()
            return
        if not regexVars.match(vars):
            print("Las variables deben de ser letras separadas por comas")
            input()
            return

        vars = [s.strip() for s in vars.split(',')]
        if not all(len(v)==1 for v in vars):
            raise ValueError("las variables no son todas de un solo caracter")
        vars = [sympy.symbols(v) for v in vars]

        defs = {
            **{ v.name : v for v in vars },
            'e'  : sympy.E,
            'pi' : sympy.pi,
        }

        try:
            expr = sympy.parse_expr(expr, local_dict=defs, transformations=
                sympy.parsing.sympy_parser.standard_transformations + (
                sympy.parsing.sympy_parser.convert_xor,
                sympy.parsing.sympy_parser.implicit_multiplication_application
            ))
        except Exception:
            print("error de syntaxis al parsear la expresion")
            input()
            return
    
        global menu
        f = Funcion(nombre, vars, expr)
        if estado:
            estado.f = f
        else:
            menu.estado = Estado(f)
            for opcion in menu.opciones:
                opcion.activa = True


    @Opcion.esperar_entrada
    @Opcion.requerir_estado
    def calcular_integral(estado: Estado):
        lims: list[tuple[float, float]] = []
        
        for var in estado.f.vars:
            a, b = 0.0, 0.0
            while True:
                print(f"Limites de la variable {var.name}")
                token = input("a, b = ")
                try:
                    a,b = [s.strip() for s in token.split(',')]
                    a = float(a)
                    b = float(b)
                    break
                except ValueError:
                    print("Ingrese dos numeros separados por una coma")
                    input()
                    continue
            lims.append((a,b))
        
        I = estado.metodo(estado.f, lims, estado.n)
        print(f"Valor aproximado de la integral: {I:.{estado.pres}f}")


    @Opcion.requerir_estado
    def modificar_argumento(estado: Estado):
        try:
            n = int(input(f"{estado.simbolo_arg} = "))
            if n < 1:
                print(f"el numero de {estado.nombre_arg} debe ser mayor o igual a 1")
                input()
            else:
                estado.n = n
        except ValueError:
            print("introduzca un entero")
            input()


    @Opcion.requerir_estado
    def modificar_decimales(estado: Estado):
        try:
            p = int(input("decimales = "))
            if p < 0:
                print("el numero de decimales debe cero o positivo")
                input()
            else:
                estado.pres = p
        except ValueError:
            print("introduzca un entero")
            input()


    @Opcion.requerir_estado
    def modificar_metodo(estado : Estado):
        def set_regla_del_trapecio(_):
            estado.metodo = integral_multiple_trapecio
            estado.simbolo_arg = 'n'
            estado.nombre_arg = "segmentos"
            estado.nombre_metodo = "Regla del Trapecio"
        def set_integracion_romberg(_):
            estado.metodo = integral_multiple_romberg
            estado.simbolo_arg = 'k'
            estado.nombre_arg = "iteraciones"
            estado.nombre_metodo = "Integracion de Romberg"

        Menu([
                Opcion("Regla del Trapecio", set_regla_del_trapecio),
                Opcion("Integracion de Romberg", set_integracion_romberg)
            ],
            clear=False  
        ).desplegar()
        

    def salir(_):
        altscreen(False)
        exit()


    def estatus(estado: Estado | None):
        print("Calculadora de Integrales Multiples")
        if not estado: return
        print(str(estado.f),
              f"No. {estado.nombre_arg}: {estado.n}",
              f"No. decimales: {estado.pres}",
              f"Metodo: {estado.nombre_metodo}",
              sep='\n'
        )

    menu = Menu([
            Opcion("Ingresar Funcion", introducir_funcion),
            Opcion("Calcular Integral", calcular_integral, activa=False),
            Opcion("Modificar Argumento", modificar_argumento, activa=False),
            Opcion("Modificar Decimales", modificar_decimales, activa=False),
            Opcion("Modificar Metodo", modificar_metodo, activa=False),
            Opcion("Salir", salir)
        ],
        pre = estatus
    )

    altscreen(True)
    while True: menu.desplegar()
