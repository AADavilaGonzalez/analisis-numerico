from ..utils.importar import *

np = importar_dependencia_opcional("numpy", auto=True)

plt = importar_dependencia_opcional(
    "matplotlib", modulo="matplotlib.pyplot", auto=True
)

LIMX = (-4, 4)
LIMY = (-2, 6)
RES = 1000

import math
f = lambda x : math.exp(x) - math.pi*x

if np and plt:
    x = np.linspace(LIMX[0]-1, LIMX[1]+1, RES)
    y = np.vectorize(f)(x)

    fig, ax = plt.subplots()
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlim(*LIMX)
    ax.set_ylim(*LIMY)
    ax.grid(True)
    ax.plot(x,y)
    plt.show()
