try:
    import sympy
except ImportError:
    print("El paquete sympy es obligatorio para correr este programa",
            "por favor instale el paquete utilizando el siguiente comando",
            "[py/python/python3] -m pip install sympy", sep="\n")
    exit()

if __name__ == "__main__":
    _ = sympy
