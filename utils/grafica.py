from .deps.np import *
from .deps.plt import *
from typing import Callable

__all__ = ["Vista", "Grafica"]

from dataclasses import dataclass
@dataclass
class Vista:
    x_min: float
    x_max: float
    y_min: float
    y_max: float

class Grafica:

    @classmethod
    def mostrar(cls, *args, **kwargs) -> None:
        plt.show(*args, **kwargs)

    @classmethod
    def cerrar(cls, grafica=None) -> None:
        if grafica: plt.close(grafica._fig)
        else: plt.close("all")

    @classmethod
    def modo_interactivo(cls, activar: bool=True) -> None:
        if activar: plt.ion()
        else: plt.ioff()

    def __remplazar(self, nombre: str, obj):
        if nombre in self._obj:
            self._obj[nombre].remove()
        self._obj[nombre] = obj

    def curva(self, nombre: str, X: list[float], Y: list[float], **kwargs) -> None:
        linea = self._ax.plot(X, Y, **kwargs)[0]
        if nombre:
            self.__remplazar(nombre, linea)

    def __init__(self, vista: Vista, res: int = 50, dt: int = 1
    ):
        self._vista = vista
        self._fig, self._ax = plt.subplots()
        self._ax.set_xlim(vista.x_min, vista.x_max)
        self._ax.set_ylim(vista.y_min, vista.y_max)
        self._res = res
        self._dt = dt
        self._obj = {}

    def ejes(self, color="black", **kwargs) -> None:
        self._ax.axhline(0, color=color, **kwargs)
        self._ax.axvline(0, color=color, **kwargs)

    def cuadricula(self, *args, **kwargs) -> None:
        self._ax.grid(*args, **kwargs)

    def punto(self, nombre: str, x: float, y: float,
        marker="o", **kwargs
    ) -> None:
        punto = self._ax.plot(x, y, marker=marker, **kwargs)[0]
        if nombre: self.__remplazar(nombre, punto)

    def linea(self, nombre: str, m: float,
        xi: float = 0, yi: float = 0, **kwargs
    ) -> None:
        xmin, xmax = self._ax.get_xlim()
        x = [xmin-1, xmax+1]
        y = [m*(i-xi)+yi for i in x]
        linea = self._ax.plot(x, y, **kwargs)[0] 
        if nombre: self.__remplazar(nombre, linea)

    def linea_horizontal(self, nombre: str, yi: float,
        **kwargs
    ) -> None:
        self.__remplazar(nombre, self._ax.axvline(yi, **kwargs))

    def linea_vertical(self, nombre: str, xi: float,
        **kwargs
    ) -> None:
        linea = self._ax.axvline(xi, **kwargs)
        if nombre: self.__remplazar(nombre, linea)

    def funcion(self, nombre, f: Callable[[float], float],
        xmin: float, xmax: float, **kwargs
    ) -> None:
        x = np.linspace(xmin, xmax, self._res)
        y = (np.vectorize(f))(x)
        funcion = self._ax.plot(x, y, **kwargs)[0] 
        if nombre: self.__remplazar(nombre, funcion)

    def ecuacion_implicita(self, nombre: str,
        f: Callable[[float,float], float],
        vista: Vista, color:str = "blue"
    ) -> None:
        x = np.linspace(vista.x_min, vista.x_max, self._res)
        y = np.linspace(vista.y_min, vista.y_max, self._res)
        x, y = np.meshgrid(x,y)
        z = np.vectorize(f)(x,y)
        ecuacion =  self._ax.contour(x,y,z, levels=[0], colors=color)
        self.__remplazar(nombre, ecuacion)

    def actualizar(self) -> None:
        self._fig.canvas.draw()

    def eliminar_objeto(self, nombre: str) -> None:
        if nombre in self._obj:
            self._obj[nombre].remove()
            del self._obj[nombre]

    def pausar(self, s: float | None = None) -> None:
        plt.pause(s if s is not None else self._dt)

if __name__ == "__main__":
    grafica = Grafica(
        Vista(-2,2,-2,2),
        res = 50
    )

    grafica.ecuacion_implicita(
        "eq1",
        lambda x,y: x**2 + y**2 - 1,
        Vista(-1,1,-1,1)
    )

    Grafica.mostrar()
