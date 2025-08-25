from typing import Self
from collections.abc import Iterator
import math

class Vector:

    decimales_str = 2

    def __init__(self, x: float | list[float], n: int | None = None,
        *, default: float = 0
    ):
        if isinstance(x, list):
            if not x:
                raise ValueError("se necesita una lista no vacia")
            n = n if n and n > 0 else len(x)
            self._dim = n if n else len(x)
            self._x = [float(x[i]) for i in range(n)]
            self._x.extend([default]*(n-len(x)))
        else:
            if not n:
                raise ValueError("se necista espeficar longitud 'n'")
            if n < 1:
                raise ValueError("'n' debe ser mayor a 0")
            self._x = [float(x)]*n
        self._dim = n

    def __iter__(self) -> Iterator:
        return iter(self._x)

    def __str__(self) -> str:
        strings = [f"{x:.{self.__class__.decimales_str}f}" for x in self._x]
        return f"({", ".join(strings)})"

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def datos(self) -> list[float]:
        return self._x

    def __getitem__(self, i: int) -> float:
        return self._x[i]

    def __setitem__(self, i: int, val: float) -> None:
        self._x[i] = val

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.dim != other.dim:
            raise ValueError(
                "los vectores deben tener las misma dimension"
            )
        return self.__class__(
            [x+y for x,y in zip(self._x, other._x)], self.dim
        )

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        if self.dim != other.dim:
            raise ValueError(
                "los vectores deben tener las misma dimension"
            )
        return self.__class__(
            [x-y for x,y in zip(self._x, other._x)], self.dim
        )

    def __mul__(self, other: float) -> Self:
        if not isinstance(other, float):
            return NotImplemented
        return self.__class__([x*other for x in self._x], self.dim)
    __rmul__ = __mul__

    def __truediv__(self, other: float) -> Self:
        if not isinstance(other, float):
            return NotImplemented
        return self.__class__([x/other for x in self._x], self.dim)
    __rtruediv__ = __truediv__

    def copiar(self) -> Self:
        return self.__class__(self._x, self.dim)

    def producto_punto(self, other: Self) -> float:
        if self.dim != other.dim:
            raise ValueError("las dimensiones deben ser iguales")
        return sum(x*y for x,y in zip(self._x, other._x))

    def magnitud(self) -> float:
        return math.sqrt(sum(x**2 for x in self._x))

