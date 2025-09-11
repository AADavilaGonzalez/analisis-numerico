import numpy as np

def minimos_cuadrados(x:np.ndarray, y:np.ndarray):
    n = len(x)
    # Minimos cuadrados
    sum_x=np.sum(x)
    sum_y=np.sum(y)
    sum_xy=np.sum(x*y)
    sum_x2=np.sum([x[i] ** 2 for i in range(n)])
    sum_y2=np.sum([y[i] ** 2 for i in range(n)])
    prom_x = np.mean(x)
    prom_y = np.mean(y)
    a1=(n * sum_xy - sum_x * sum_y)/(n * sum_x2 - sum_x ** 2)
    a0 = prom_y - a1 * prom_x
    f = lambda x: a0 + a1 * x
    # Coeficiente de Correlacion
    r:float = (n * sum_xy - sum_x * sum_y) / (np.sqrt(n * sum_x2 - sum_x ** 2) * np.sqrt(n * sum_y2 - sum_y ** 2))
    return f, r

