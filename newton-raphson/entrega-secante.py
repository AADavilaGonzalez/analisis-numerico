import importlib
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Any

def importar_dependencia_opcional(
    paquete: str,
    modulo: str = "",
    objeto: str = "",
    advertencia: str = "",
    tmpdir: str = "",
    auto: bool = False
) -> Any:

    modulo = modulo or paquete

    #Agregar tmpdir a path para checar si esta ahi
    tmp_path = Path(tmpdir) if tmpdir else Path(sys.argv[0]).parent/"lib"
    tmp_path_str = str(tmp_path.resolve())
    agregado_a_path = False
    if tmp_path.is_dir() and not tmp_path_str in sys.path:
            sys.path.append(tmp_path_str)
            agregado_a_path = True

    if not find_spec(modulo.partition(".")[0]):

        def instalar_paquete(instalar_global: bool = False) -> bool:
            nonlocal agregado_a_path
            args = [sys.executable, "-m", "pip", "install", paquete]
            if not instalar_global:
                if not agregado_a_path:
                    sys.path.append(tmp_path_str)
                    agregado_a_path = True
                args.extend(["--target", tmp_path_str])
            return subprocess.run(args).returncode == 0

        def dialogo() -> bool:
            print(f"El paquete '{paquete}' no ha sido encontrado.")
            if advertencia: print(advertencia)

            print("Desea instalar el paquete en el entorno actual?(s/N)")
            if input().lower().startswith("s"):
                return instalar_paquete(instalar_global=True)

            print( "Desea instalar el paquete de forma externa en",
                    f"{tmp_path_str}?(s/N)", sep="\n")
            if input().lower().startswith("s"):
                return instalar_paquete()

            return False

        instalar = instalar_paquete if auto else dialogo
        if not instalar():
            if not auto: print(f"No se ha instalado '{paquete}'")
            if agregado_a_path: sys.path.pop()
            return None

    try:
        modulo_encontrado = importlib.import_module(modulo)
        if objeto:
            return getattr(modulo_encontrado, objeto)
        else:
            return modulo_encontrado
    except Exception:
        if agregado_a_path: sys.path.pop()
        raise

class Tabla:

    def __init__(self, *args:str, minlen=10, floatpres=6):
        self.campos = tuple(str(arg) for arg in args)
        campos_con_formato = tuple(campo.center(minlen) for campo in self.campos)
        self.espaciados = tuple(len(campo) for campo in campos_con_formato)
        self._encabezado = " | ".join(campos_con_formato)
        self.floatpres = floatpres

    def encabezado(self) -> str:
        return self._encabezado

    def fila(self, *args) -> str:

        def formatear(arg, l:int):
            match arg:
                case int():
                    return f"{arg:{l}d}"
                case float():
                    return f"{arg:{l}.{self.floatpres}f}"
                case _:
                    return str(arg)[:l].rjust(l)

        if len(args) != len(self.campos):
            raise ValueError("Provea la cantidad de argumentos conforme a los campos")
        celdas = [formatear(args[i], self.espaciados[i]) for i in range(len(args))]
        return " | ".join(celdas)


import math
from typing import Callable, Iterator

FuncionReal = Callable[[float], float]

f: FuncionReal = lambda x: math.exp(x)-math.pi*x

def raiz_por_secante(
    f: FuncionReal,
    x0: float,
    x1: float,
    err: float
) -> Iterator[tuple[float, float, float]]:

    prev = x0
    act = x1
    while True:
        m_inv = (act-prev)/(f(act)-f(prev))
        prev, act = act, act - f(act)*m_inv
        err_act = math.fabs(act-prev)/act
        yield act, err_act, m_inv
        if err_act <= err:
            return

np = importar_dependencia_opcional("numpy")

plt = importar_dependencia_opcional(
    "matplotlib", modulo="matplotlib.pyplot"
)

def buscar_raiz(
    f: FuncionReal,
    x0: float,
    err: float,
    x1: float | None = None
):

    tabla = Tabla("xi-1", "xi", "xi+1", "error")
    print(tabla.encabezado())
    prev = x0
    act = x1 or x0+1
    iterador = raiz_por_secante(f,prev, act, err)

    fig: Any = None
    ax: Any = None
    TIEMPO_ESPERA = 2

    if np and plt:
        x = np.linspace(-5, 5, 100)
        y = np.vectorize(f)(x)
        _, ax = plt.subplots()
        ax.axhline(0, color="black", linewidth=1)
        ax.axvline(0, color="black", linewidth=1)
        ax.set_xlim(-4, 4)
        ax.set_ylim(-2, 6)
        ax.grid(True)
        ax.plot(x,y, color="blue")
        pts = ax.scatter(
            [prev, act],
            [0, 0],
            color="red"
        )
        plt.show(block=False)
        plt.pause(TIEMPO_ESPERA)
        pts.remove()

    for sig, err_act, m_inv in iterador:
        print(tabla.fila(prev, act, sig, err_act))

        if np and plt:
            pts = ax.scatter(
                [prev, act], [0,0], color="green"
            )
            p = ax.scatter(
                [sig],[0], color="red"
            )
            m = 1/m_inv
            xmin, xmax = ax.get_xlim()
            x = [xmin-1, xmax+1]
            y = [m*(i-sig) for i in x]
            l_prev = ax.axvline(prev, color="black",
                linestyle="--", linewidth=1)
            l_act = ax.axvline(act, color="black",
                linestyle="--", linewidth=1)
            sec, = ax.plot(x, y, color="green")
            plt.draw()
            plt.pause(TIEMPO_ESPERA)
            pts.remove()
            p.remove()
            l_prev.remove()
            l_act.remove()
            sec.remove()

        prev, act = act, sig

    if np and plt:
        plt.close(fig)

if __name__ == "__main__":
    ERROR = 0.000001
    print("Tabla Raiz 1")
    buscar_raiz(f, 0, ERROR)
    print()
    print("Tabla Raiz 2")
    buscar_raiz(f, 2, ERROR)
