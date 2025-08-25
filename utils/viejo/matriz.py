from .vector import *
import copy

class Matriz:
    decimales_str = 2

    def __init__(self, x: float | list[list[float]], *,
        m: int | None = None, n: int | None = None,
        default: float = 0
    ):
        if isinstance(x, list):
            if not x:
                raise ValueError("se necesita una list no vacia")
            m = len(x) if m is None else m
            if m < 1: raise ValueError("'m' debe ser mayor a 0")
            n = len(x[0]) if n is None else n
            if n < 1: raise ValueError("'n' debe ser mayor a 0")
            self._x = [Vector(fila, n) for fila in x]
            self._x.extend([Vector(default,n) for _ in range(m-len(x))])
        else:
            if not n or not m:
                raise ValueError("Especifique los valores de 'm' y 'n'")
            if m < 1: raise ValueError("'m' debe ser mayor a 0")
            if n < 1: raise ValueError("'n' debe ser mayor a 0")
            self._x = [Vector(default, n) for _ in range(m)]
            for i in range(min(n,m)):
                self._x[i][i] = x
        self._dim = m, n

    def __str__(self) -> str:
        vec_strings = []
        for vec in self._x:
            strings = [f"{x:.{self.__class__.decimales_str}f}" for x in vec]
            vec_strings.append(f"| {", ".join(strings)} |")
        return "\n".join(vec_strings)

    @property
    def dim(self) -> tuple[int, int]:
        return self._dim

    def __getitem__(self, i: int) -> Vector:
        return self._x[i]

    def __add__(self, other: Self) -> Self:
        if self.dim != other.dim:
            raise ValueError("matrices con dimension diferente")
        m, n = self.dim
        mat = self.__class__(0,m=m, n=n)
        for i in range(m):
            for j in range(n):
                mat[i][j] = self[i][j] + other[i][j]
        return mat

    def __sub__(self, other: Self) -> Self:
        if self.dim != other.dim:
            raise ValueError("matrices con dimension diferente")
        m, n = self.dim
        mat = self.__class__(0,m=m, n=n)
        for i in range(m):
            for j in range(n):
                mat[i][j] = self[i][j] - other[i][j]
        return mat

    def __mul__(self, other: float) -> Self:
        m, n = self.dim
        mat = self.__class__(0,m=m, n=n)
        for i in range(m):
            for j in range(n):
                mat[i][j] = self[i][j] * other
        return mat

    def __truediv__(self, other: float) -> Self:
        m, n = self.dim
        mat = self.__class__(0,m=m, n=n)
        for i in range(m):
            for j in range(n):
                mat[i][j] = self[i][j] / other
        return mat

    def copiar(self) -> Self:
        m, n = self.dim
        mat = [copy.deepcopy(vec._x) for vec in self._x]
        return self.__class__(mat, m=m, n=n)

    def transponer(self) -> Self:
        m, n = self.dim
        mat = self.__class__(0, m=n, n=m)
        for i in range(m):
            for j in range(n):
                mat[i][j] = self[j][i]
        return mat

    def det(self) -> float:
        m, n = self.dim
        if m != n:
            raise ValueError("matriz no cuadrada")

        VALOR_PIVOTE_MIN = 1e-12
        mult = 1.0
        mat = self.copiar()

        for i in range(n-1):

            if math.fabs(mat[i][i]) < VALOR_PIVOTE_MIN:
                for j in range(i+1,m):
                    if math.fabs(mat[j][i]) >= VALOR_PIVOTE_MIN:
                        mat._x[i], mat._x[j] = mat._x[j], mat._x[i]
                        mult *= -1
                        break
                else:
                    return 0.0

            for j in range(i+1, m):
                factor = mat[j][i]/mat[i][i]
                for k in range(i,n):
                    mat[j][k] -= factor*mat[i][k]

        return mult*math.prod(mat[i][i] for i in range(n))

    @classmethod
    def producto(cls, izq:Self, der: Self) -> Self:
        m, n1 = izq.dim
        n2, p = der.dim
        if n1 != n2:
            raise ValueError("matrices incompatibles")
        mat = [[0.0]*p for _ in range(m)]
        for i in range(p):
            columna = Vector([der[k][i] for k in range(n1)])
            for j in range(m):
                mat[j][i] = izq[j].producto_punto(columna)
        return cls(mat, m=m, n=p)


if __name__=="__main__":
    mat1 = Matriz([
        [1,0],
        [1,0]
    ])

    mat2 = Matriz(0, m=2, n=2)

    print(mat1)
    print(mat2)

    print()
    mat2[0][0] = mat1[0][0]

    print(mat1)
    print(mat2)
