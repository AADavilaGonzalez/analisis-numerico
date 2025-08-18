from ..utils.importar import *

np = importar_dependencia_opcional("numpy", auto=True)

plt = importar_dependencia_opcional(
    "matplotlib", modulo="matplotlib.pyplot", auto=True
)

FuncAnimation = importar_dependencia_opcional(
    "matplotlib", modulo="matplotlib.animation",
    objeto="FuncAnimation", auto=True
)

if np and plt and FuncAnimation:
    x = np.linspace(-2*np.pi, 2*np.pi, 1000)
    y = np.sin(x)

    fig, ax = plt.subplots()
    sine_line, = ax.plot(x,y)

    def actualizar(frame):
        mult = np.sin(180*frame/np.pi)
        sine_line.set_ydata(y+mult)
        return sine_line,

    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True)

    anim = FuncAnimation(fig, actualizar, frames=100, interval=50, blit=True)

    plt.show()
