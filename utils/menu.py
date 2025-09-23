from .ansi import *

from typing import Callable, TypeVar, Generic, Iterator

__all__ = ["Accion", "Opcion", "Menu"]

T = TypeVar("T")

Accion = Callable[[T | None], None]
noOp: Accion = lambda _ : None

class Opcion(Generic[T]):

    def __init__(self,
        nombre: str,
        accion: Accion[T],
        *,
        activa: bool = True
    ):
        self.nombre = nombre
        self.accion = accion
        self.activa = activa

    @staticmethod
    def limpiar_pantalla(f: Accion[T]) -> Accion[T]:
        def wrapper(estado: T | None) -> None:
            clear()
            f(estado)
        return wrapper
            
    @staticmethod
    def esperar_entrada(f: Accion[T]) -> Accion[T]:
        def wrapper(estado: T | None) -> None:
            f(estado)
            input()
        return wrapper

    @staticmethod
    def requerir_estado(f: Callable[[T], None]) -> Accion[T]:
        def wrapper(estado: T | None) -> None:
            assert estado is not None
            f(estado)
        return wrapper

class Menu(Generic[T]):

    def __init__(self,
        opciones: list[Opcion[T]],
        estado: T | None = None,
        pre: Accion[T] = noOp,
        pos: Accion[T] = noOp,
        clear: bool = True,
        indices: bool = True,
        sangria: int = 0,
        prompt: str = "> ",
        val_inv: Accion[T] = noOp,
        sol_conf: Callable[[list[Opcion[T]]], Accion[T]] | None = None
    ):
        self.estado = estado
        self.opciones = opciones
        self.pre = pre
        self.pos = pos

        self.clear = clear

        self.indexable = indices
        self.mostrar_indices = indices

        self.sangria_ops = sangria
        self.sangria_prompt = sangria

        self.prompt = prompt

        self.val_inv = val_inv
        self.sol_conf = sol_conf or type(self).__solucionar_conflicto

    def __opciones_activas(self) -> Iterator[Opcion[T]]:
        return (op for op in self.opciones if op.activa)

    @staticmethod
    def __solucionar_conflicto(opciones: list[Opcion[T]]) -> Accion[T]:
        return opciones[0].accion


    def mostrar(self) -> None:
        if self.clear: clear()
        if self.pre: self.pre(self.estado)
        for i, opcion in enumerate(self.__opciones_activas()):
            linea = " " * self.sangria_ops
            if self.mostrar_indices:
                linea += f"{i+1}. "
            linea += opcion.nombre
            print(linea)
        if self.pos: self.pos(self.estado)


    def seleccionar(self) -> None:

        print(" " * self.sangria_prompt, end="")
        token = input(self.prompt).strip()
        if not token:
            self.val_inv(self.estado)
            return

        accion = None
        opciones_activas = tuple(self.__opciones_activas())

        if self.indexable and token.isdigit():
            i = int(token)
            if 1 <= i <= len(opciones_activas):
                accion = opciones_activas[i-1].accion
        else:  
            token = token.lower()
            candidatos = [
                op for op in opciones_activas
                if op.nombre.strip().lower().startswith(token)
            ]
            if len(candidatos) == 1:
                accion = candidatos[0].accion
            elif len(candidatos) != 0:
                accion = self.sol_conf(candidatos)

        if accion:
            accion(self.estado)
        else:
            self.val_inv(self.estado)


    def desplegar(self) -> None:
        self.mostrar()
        self.seleccionar()

    def desplegar_mientras(self, cond: Callable[[],bool]) -> None:
        while cond():
            self.mostrar()
            self.seleccionar()


if __name__ == "__main__":

    print("Entrando a main")

    from dataclasses import dataclass
    @dataclass
    class Estado:
        primero: int
        segundo: int

    estado = Estado(0,0)

    @Opcion.requerir_estado
    def instrucciones(estado) -> None:
        print("Primero lo primero y segundo lo segundo...")
        print(f"primero: {estado.primero}")
        print(f"segundo: {estado.segundo}")

    @Opcion.requerir_estado
    def incrementar_primero(estado: Estado) -> None: estado.primero += 1
    @Opcion.requerir_estado
    def decrementar_primero(estado: Estado) -> None: estado.primero -= 1
    @Opcion.requerir_estado
    def incrementar_segundo(estado: Estado) -> None: estado.segundo += 1
    @Opcion.requerir_estado
    def decrementar_segundo(estado: Estado) -> None: estado.segundo -= 1

    menu = Menu([
            Opcion("Incrementar primero", incrementar_primero),
            Opcion("Decrementar primero", decrementar_primero),
            Opcion("Incrementar segundo", incrementar_segundo),
            Opcion("Decrementar segundo", decrementar_segundo)
        ],
        estado = estado,
        pre = instrucciones
    )

    while True:
        menu.mostrar()
        menu.seleccionar()
