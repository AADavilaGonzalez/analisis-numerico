import numpy as np
import os
import re
import matplotlib.pyplot as plt

def parse_puntos(punto:str):
    match = re.match(r'\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*', punto)
    if not match:
        raise ValueError('Ingrese un formato valido.')
    x,y = match.groups()
    return float(x), float(y)

def cleaner():
    os.system('cls' if os.name == 'nt' else 'clear')

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



def main():
    cleaner()
    print('\n **********AJUSTE DE CURVAS O PUNTOS********\n*************POR REGRESION LINEAL*************')
    n = int(input('\nIngrese el total de puntos> '))

    X = []
    Y = []

    for i in range (n):
        print('\nFormato para introducir el punto seria: x,y. Ejemplo: 1,-2')
        punto = input(f'Introduzca el punto #{i+1}> ')
        eje_x,eje_y = parse_puntos(punto)
        X.append(eje_x)
        Y.append(eje_y)
        print(f'Coordenada {eje_x}, {eje_y} agregada con exito.')

    X = np.array(X)
    Y = np.array(Y)

    funcion, correlacion_r = minimos_cuadrados(X, Y)
    
    x_predecida = float(input('\nIngrese la x a estimar en la recta aproximada> '))

    print(f'El valor de {x_predecida} en la funcion es de aproximadamente {round(funcion(x_predecida),4)}')
    print(f'Con un coeficiente de correlacion r = {round(correlacion_r, 4)}')
    input('\nDe enter para visualizar la grafica...')


    plt.scatter(X, Y, color='blue', label='Puntos dados')

    x_vals = np.linspace(min(X), max(X), 100)
    plt.plot(x_vals, funcion(x_vals), color='red', label='Recta ajustada')
    plt.scatter(x_predecida, funcion(x_predecida), color='green', s=100, label=f'Predicción ({x_predecida},{funcion(x_predecida):.2f})', zorder=5)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Regresion lineal por minimos cuadrados')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()
