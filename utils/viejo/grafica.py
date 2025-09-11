from .importar import *
from typing import Callable


class Grafica:

    np = importar_dependencia_opcional("numpy")
    plt = importar_dependencia_opcional("matplotlib", modulo="matplotlib.pyplot")

    @classmethod
    def modulo_activo(cls) -> bool:
        return bool(cls.np and cls.plt)

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

    @classmethod
    @requiere_modulo_activo
    def mostrar(cls, *args, **kwargs) -> None:
        cls.plt.show(*args, **kwargs)

    @classmethod
    @requiere_modulo_activo
    def cerrar(cls, grafica=None) -> None:
        if grafica: cls.plt.close(grafica._fig)
        else: cls.plt.close("all")

    @classmethod
    @requiere_modulo_activo
    def modo_interactivo(cls, activar: bool=True) -> None:
        if activar: cls.plt.ion()
        else: cls.plt.ioff()

    @requiere_modulo_activo
    def __init__(self, xmin: float, xmax: float,
        ymin: float, ymax: float, res: int = 10, dt: int = 1
    ):
        self._fig, self._ax = self.plt.subplots()
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
        punto = self._ax.plot(x, y, marker=marker, **kwargs)[0]
        if nombre: self.__remplazar(nombre, punto)

    @requiere_modulo_activo
    def linea(self, nombre: str, m: float,
        xi: float = 0, yi: float = 0, **kwargs
    ) -> None:
        xmin, xmax = self._ax.get_xlim()
        x = [xmin-1, xmax+1]
        y = [m*(i-xi)+yi for i in x]
        linea = self._ax.plot(x, y, **kwargs)[0] 
        if nombre: self.__remplazar(nombre, linea)

    @requiere_modulo_activo
    def linea_horizontal(self, nombre: str, yi: float,
        **kwargs
    ) -> None:
        self.__remplazar(nombre, self._ax.axvline(yi, **kwargs))

    @requiere_modulo_activo
    def linea_vertical(self, nombre: str, xi: float,
        **kwargs
    ) -> None:
        linea = self._ax.axvline(xi, **kwargs)
        if nombre: self.__remplazar(nombre, linea)

    @requiere_modulo_activo
    def funcion(self, nombre, f: Callable[[float], float],
        xmin: float, xmax: float, **kwargs
    ) -> None:
        x = self.np.linspace(xmin, xmax, int((xmax-xmin)*self._res))
        y = (self.np.vectorize(f))(x)
        funcion = self._ax.plot(x, y, **kwargs)[0] 
        if nombre: self.__remplazar(nombre, funcion)

    @requiere_modulo_activo
    def ecuacion_implicita(self, nombre: str, f: Callable[[float,float], float],
        xmin: float, xmax: float, ymin: float, ymax: float, color:str = "blue"
    ) -> None:
        x = self.np.linspace(xmin, xmax, self._res)
        y = self.np.linspace(ymin, ymax, self._res)
        x, y = self.np.meshgrid(x,y)
        z = self.np.vectorize(f)(x,y)
        ecuacion =  self._ax.contour(x,y,z, levels=[0], colors=color)
        self.__remplazar(nombre, ecuacion)

    @requiere_modulo_activo
    def actualizar(self) -> None:
        self._fig.canvas.draw()

    @requiere_modulo_activo
    def eliminar_objeto(self, nombre: str) -> None:
        if nombre in self._obj:
            self._obj[nombre].remove()
            del self._obj[nombre]

    @requiere_modulo_activo
    def pausar(self, tiempo: float | None = None) -> None:
        self.plt.pause(tiempo if tiempo is not None else self.dt)

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
