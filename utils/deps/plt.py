try:
    import matplotlib
except ImportError:
    print("El paquete matplotlib es obligatorio para correr este programa",
          "por favor instale el paquete utilizando el siguiente comando",
          "[py/python/python3] -m pip install matplotlib", sep="\n")
    exit()

try:
    import tkinter
    matplotlib.use("TkAgg")
except ImportError:
    print("Es obligatorio tener una version de python con Tkinter para",
          "correr este programa. Instale una version de python con soporte",
          "para la libreria Tkinter", sep="\n")
    exit()

del matplotlib
del tkinter
from matplotlib import pyplot as plt

if __name__ == "__main__":
    _ = plt
