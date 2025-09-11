try:
    import numpy as np
except ImportError:
    print("El paquete numpy es obligatorio para correr este programa",
            "por favor instale el paquete utilizando el siguiente comando",
            "[py/python/python3] -m pip install numpy", sep="\n")
    exit()

if __name__ == "__main__":
    _ = np
