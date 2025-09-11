import os
from typing import Callable, TypeVar, Generic, Iterator

__all__ = ["clear", "Accion", "Opcion", "Menu"]

match os.name:
    case "posix":
        clear = lambda: os.system("clear")
    case "nt":
        clear = lambda: os.system("cls")
    case _:
        clear = lambda: None

T = TypeVar("T")

Accion = Callable[[T], None]

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

class Menu(Generic[T]):

    def __init__(self,
        estado: T,
        opciones: list[Opcion[T]],
        pre: Accion[T] | None = None,
        pos: Accion[T] | None = None,
        clear: bool = True,
        indices: bool = True,
        sangria: int = 0,
        prompt: str = "> ",
        val_inv: Accion[T] | None = None,
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

        self.val_inv = val_inv or type(self).__valor_invalido
        self.sol_conf = sol_conf or type(self).__solucionar_conflicto

    def __opciones_activas(self) -> Iterator[Opcion[T]]:
        return (op for op in self.opciones if op.activa)

    @staticmethod
    def __valor_invalido(_: T) -> None:
        return

    @staticmethod
    def __solucionar_conflicto(opciones: list[Opcion[T]]) -> Accion[T]:
        return opciones[0].accion

    @staticmethod
    def limpiar_pantalla(f: Accion[T]) -> Accion[T]:
        def wrapper(estado: T) -> None:
            clear()
            f(estado)
        return wrapper
            
    @staticmethod
    def esperar_entrada(f: Accion[T]) -> Accion[T]:
        def wrapper(estado: T) -> None:
            f(estado)
            input()
        return wrapper

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

    def desplegar_mientras(self, cond: Callable[[T], bool]) -> None:
        while cond(self.estado):
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

    def instrucciones(estado:Estado) -> None:
        print("Primero lo primero y segundo lo segundo...")
        print(f"primero: {estado.primero}")
        print(f"segundo: {estado.segundo}")

    def incrementar_primero(estado: Estado) -> None: estado.primero += 1
    def decrementar_primero(estado: Estado) -> None: estado.primero -= 1
    def incrementar_segundo(estado: Estado) -> None: estado.segundo += 1
    def decrementar_segundo(estado: Estado) -> None: estado.segundo -= 1

    menu = Menu(estado, [
        Opcion("Incrementar primero", incrementar_primero),
        Opcion("Decrementar primero", decrementar_primero),
        Opcion("Incrementar segundo", incrementar_segundo),
        Opcion("Decrementar segundo", decrementar_segundo)
        ],
        pre = instrucciones
    )

    import os
    while True:
        os.system("clear")
        menu.mostrar()
        menu.seleccionar()
