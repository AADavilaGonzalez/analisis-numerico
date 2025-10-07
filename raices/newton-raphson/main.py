from ...utils.tabla import *
from ...utils.viejo.importar import *

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
