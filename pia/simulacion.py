from typing import Hashable
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np

@dataclass
class Punto:
    x: float
    y: float

@dataclass
class ObjetoGravitacional:
    id: Hashable
    m: float
    r: Punto
    v: Punto

class CalidadSimulacion(Enum):
    BAJA = auto(),
    MEDIA = auto(),
    ALTA = auto()

class SimulacionGravitacional2D:

    G = 1
    COLS = 5
    POLITICA_DE_CRECIMIENTO = 2

    def __init__(
        self,
        objetos: list[ObjetoGravitacional],
        h: float,
        *,
        calidadSimulacion: CalidadSimulacion,
        capacidadInicial: int = 1
    ):

        self._h = h
        self._n = len(objetos)
        self._capacidad = max(capacidadInicial, self._n)
        self._buffer = np.empty((self._capacidad, self.COLS), dtype=np.float64)

        self._M = self._buffer[:,0]
        self._M[:self._n] = [obj.m for obj in objetos]

        self._R = self._buffer[:, 1:3]
        self._R[:,0] = [obj.r.x for obj in objetos]
        self._R[:,1] = [obj.r.y for obj in objetos]

        self._V = self._buffer[:, 3:5]
        self._V[:,0] = [obj.v.x for obj in objetos]
        self._V[:,1] = [obj.v.y for obj in objetos]
  
        self._posiciones = {
            obj.id : i for i, obj in enumerate(objetos)
        }
        
        self.calidadSimulacion = calidadSimulacion


    def add_objeto(self, obj: ObjetoGravitacional) -> bool:
        if obj.id in self._posiciones: return False
        cols_obj = [obj.m, obj.r.x, obj.r.y, obj.v.x, obj.v.y]
        if self._n >= self._capacidad:
            nueva_capacidad = int(self._capacidad * self.POLITICA_DE_CRECIMIENTO)+1
            nuevo_buffer = np.empty((nueva_capacidad, self.COLS), dtype=np.float64)
            nuevo_buffer[:self._n] = self._buffer
            self._buffer = nuevo_buffer
            self._capacidad = nueva_capacidad
            self._M = self._buffer[:, 0]
            self._R = self._buffer[:, 1:3]
            self._V = self._buffer[:, 3:5]
        self._buffer[self._n, :] = cols_obj
        self._posiciones[obj.id] = self._n
        self._n += 1
        return True


    def delete_objeto(self, id: Hashable) -> bool:
        i = self._posiciones.get(id)
        if i is None:
            return False
        self._buffer[:, i:self._n-1] = self._buffer[:, i+1:self._n]
        self._n -= 1
        return True
            

    def get_objeto(self, id: Hashable) -> ObjetoGravitacional | None:
        i = self._posiciones.get(id)
        if i is None: return None
        return ObjetoGravitacional(
           id = id,
           m = self._M[i],
           r = Punto(self._R[i,0], self._R[i,1]),
           v = Punto(self._V[i,0], self._V[i,1])
        )


    def set_objeto(self, obj: ObjetoGravitacional) -> None:
        i = self._posiciones.get(id)
        if i is None:
            self.add_objeto(obj)
            return
        self._M[i] = obj.m
        self._R[i,0] = obj.r.x
        self._R[i,1] = obj.r.y
        self._V[i,0] = obj.v.x
        self._V[i,1] = obj.v.y
   

    def __aceleracciones(
        self,
        R: np.ndarray, # (n,2),
    ) -> np.ndarray:
        A = np.empty((self._n,2)) # (n,2)
        for i in range(self._n):
            R_dist = R - R[i] # (n, 2) : rj - ri
            R_mag_cuad = np.sum(R_dist**2, axis=1) # (n, 1) : |rj-ri|^2
            R_mag_cuad[i] = 1.0 # Evitar dividir por cero
            factores = self._M / R_mag_cuad**1.5 # (n,) : mj / |rj-ri|^3
            aceleraciones = factores[:, np.newaxis] * R_dist # (n,2) : mj(rj-ri)/|rj-ri|^3
            A[i] = self.G*np.sum(aceleraciones, axis=0) # (2,) : G*sum(...)
        return A # (n,2)


    def euler(self) -> None:
        self._R += self._V*self._h
        self._V += self.__aceleracciones(self._R)*self._h

    def punto_medio(self) -> None:
        m_R = self._R + self._V*self._h/2
        m_V = self._V + self.__aceleracciones(self._R)*self._h/2

        self._R += m_V*self._h
        self._V += self.__aceleracciones(m_R)*self._h
    
    def rk4(self):
        k1_R = self._V
        k1_V = self.__aceleracciones(self._R)

        k2_R = self._V + self._h/2*k1_V
        k2_V = self.__aceleracciones(self._R+self._h/2*k1_R)

        k3_R = self._V + self._h/2 * k2_V
        k3_V = self.__aceleracciones(self._R + self._h/2 * k2_R)

        k4_R = self._V + self._h * k3_V
        k4_V = self.__aceleracciones(self._R + self._h*k3_R)

        self._R += self._h/6*(k1_R+2*k2_R+2*k3_R+k4_R)
        self._V += self._h/6*(k1_V+2*k2_V+2*k3_V+k4_V)

    def avanzarSimulacion(self) -> None:
        match(self.calidadSimulacion):
            case CalidadSimulacion.BAJA: self.euler()
            case CalidadSimulacion.MEDIA: self.punto_medio()
            case CalidadSimulacion.ALTA: self.rk4()

