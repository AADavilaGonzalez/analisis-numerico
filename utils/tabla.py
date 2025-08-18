class Tabla:

    def __init__(self, *args:str, minlen=10, floatpres=6):
        self.campos = tuple(str(arg) for arg in args)
        campos_con_formato = tuple(campo.center(minlen) for campo in self.campos)
        self.espaciados = tuple(len(campo) for campo in campos_con_formato)
        self._encabezado = " | ".join(campos_con_formato)
        self.floatpres = floatpres

    def encabezado(self) -> str:
        return self._encabezado

    def fila(self, *args) -> str:

        def formatear(arg, l:int):
            match arg:
                case int():
                    return f"{arg:{l}d}"
                case float():
                    return f"{arg:{l}.{self.floatpres}f}"
                case _:
                    return str(arg)[:l].rjust(l)

        if len(args) != len(self.campos):
            raise ValueError("Provea la cantidad de argumentos conforme a los campos")
        celdas = [formatear(args[i], self.espaciados[i]) for i in range(len(args))]
        return " | ".join(celdas)
