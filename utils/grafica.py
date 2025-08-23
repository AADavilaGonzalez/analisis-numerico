from .tipos import *
from .importar import *

np = importar_dependencia_opcional("numpy")
plt = importar_dependencia_opcional("matplotlib", modulo="matplotlib.pyplot")

class Grafica:

    @staticmethod
    def modulo_activo() -> bool:
        return bool(np and plt)

    @staticmethod
    def requiere_modulo_activo(f: Callable):
        def wrapper(*args, **kwargs):
            if Grafica.modulo_activo():
                f(*args, **kwargs)
        return wrapper

    def __remplazar(self, nombre: str, obj):
        if nombre in self._obj:
            self._obj[nombre].remove()
        self._obj[nombre] = obj

    @staticmethod
    @requiere_modulo_activo
    def mostrar(*args, **kwargs) -> None:
        plt.show(*args, **kwargs)

    @staticmethod
    @requiere_modulo_activo
    def cerrar(grafica=None) -> None:
        if grafica: plt.close(grafica._fig)
        else: plt.close("all")

    @requiere_modulo_activo
    def __init__(self, xmin: float, xmax: float,
        ymin: float, ymax: float, res: int = 10, dt: int = 1
    ):
        self._fig, self._ax = plt.subplots()
        self._ax.set_xlim(xmin, xmax)
        self._ax.set_ylim(ymin, ymax)
        self._res = res
        self.dt = dt

        self._obj = {}

    @requiere_modulo_activo
    def ejes(self, color="black", **kwargs) -> None:
        self._ax.axhline(0, color=color, **kwargs)
        self._ax.axvline(0, color=color, **kwargs)

    @requiere_modulo_activo
    def cuadricula(self, *args, **kwargs) -> None:
        self._ax.grid(*args, **kwargs)

    @requiere_modulo_activo
    def punto(self, nombre: str, x: float, y: float,
        marker="o", **kwargs
    ) -> None:
        self.__remplazar(nombre,
            self._ax.plot(x, y, marker=marker, **kwargs)[0]
        )

    @requiere_modulo_activo
    def linea(self, nombre: str, m: float,
        xi: float = 0, yi: float = 0, **kwargs
    ) -> None:
        xmin, xmax = self._ax.get_xlim()
        x = [xmin-1, xmax+1]
        y = [m*(i-xi)+yi for i in x]
        self.__remplazar(nombre, self._ax.plot(x, y, **kwargs)[0])

    @requiere_modulo_activo
    def linea_horizontal(self, nombre: str, yi: float,
        **kwargs
    ) -> None:
        self.__remplazar(nombre, self._ax.axvline(yi, **kwargs))

    @requiere_modulo_activo
    def linea_vertical(self, nombre: str, xi: float,
        **kwargs
    ) -> None:
        self.__remplazar(nombre, self._ax.axvline(xi, **kwargs))

    @requiere_modulo_activo
    def funcion(self, nombre, f: FuncionR1R1,
        xmin: float, xmax: float, **kwargs
    ) -> None:
        x = np.linspace(xmin, xmax, int((xmax-xmin)*self._res))
        y = np.vectorize(f)(x)
        self.__remplazar(nombre, self._ax.plot(x, y, **kwargs)[0])

    @requiere_modulo_activo
    def ecuacion_implicita(self, nombre: str, f: FuncionR2R1,
        xmin: float, xmax: float, ymin: float, ymax: float, color:str = "blue"
    ) -> None:
        x = np.linspace(xmin, xmax, self._res)
        y = np.linspace(ymin, ymax, self._res)
        x, y = np.meshgrid(x,y)
        z = np.vectorize(f)(x,y)
        self.__remplazar(nombre,
            self._ax.contour(x,y,z, levels=[0], colors=color)
        )

    @requiere_modulo_activo
    def actualizar(self) -> None:
        self._fig.canvas.draw()

    @requiere_modulo_activo
    def eliminar_objeto(self, nombre: str) -> None:
        if nombre in self._obj:
            self._obj[nombre].remove()
            del self._obj[nombre]

    @requiere_modulo_activo
    def pausar(self) -> None:
        plt.pause(self.dt)

if __name__ == "__main__":
    grafica = Grafica(
        xmin=-2,
        xmax=2,
        ymin=-2,
        ymax=2,
        res = 50
    )

    grafica.ecuacion_implicita(
        "eq1",
        lambda x,y: x**2 + y**2 - 1,
        xmin = -1,
        xmax = 1,
        ymin = -1,
        ymax = 1
    )

    Grafica.mostrar()
