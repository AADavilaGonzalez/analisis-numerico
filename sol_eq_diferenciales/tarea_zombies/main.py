from ...utils.equipo import *
from ...utils.ansi import *
from ...utils.menu import *
from ...utils.tabla import *
from ...utils.deps.np import *
from ...utils.deps.sympy import *
from ...utils.grafica import *

from typing import Callable

VectorFuncion = Callable[[float, np.ndarray], np.ndarray]

def euler(f: VectorFuncion, t: float, y: np.ndarray, h: float) -> np.ndarray:
    return y + f(t, y) * h

def runge_kutta_orden_4(f: VectorFuncion, t: float, y: np.ndarray, h: float) -> np.ndarray:
    """Aplica RK4 a un sistema de EDOs."""
    k1 = f(t, y)
    k2 = f(t + 0.5 * h, y + 0.5 * k1 * h)
    k3 = f(t + 0.5 * h, y + 0.5 * k2 * h)
    k4 = f(t + h, y + k3 * h)
    return y + (k1 + 2*k2 + 2*k3 + k4) * h / 6

def modelo_szr(t: float, y: np.ndarray, beta: float, alpha: float, zeta: float) -> np.ndarray:
    S, Z, R = y[0], y[1], y[2]
    
    #ecuaciones dadas
    dS_dt = -beta * S * Z
    dZ_dt = beta * S * Z - alpha * S * Z + zeta * R
    dR_dt = alpha * S * Z - zeta * R
    
    return np.array([dS_dt, dZ_dt, dR_dt])

def simular_sistema(metodo: Callable, f: VectorFuncion, y0: np.ndarray, t_fin: float, h: float):
    #calcular numero de pasos
    n_pasos = int(t_fin / h)
    
    # Prepara arrays para guardar los resultados
    # Un array 1D para el tiempo
    t_valores = np.linspace(0, t_fin, n_pasos + 1)
    
    # Un array 2D para S, Z, R
    y_valores = np.zeros((n_pasos + 1, len(y0)))
    y_valores[0] = y0 #nuestra condiciion inicial
    
    #el vector Y actual
    y = y0
    
    for i in range(n_pasos):
        t = t_valores[i]
        y = metodo(f, t, y, h)
        y_valores[i+1] = y
        
    return t_valores, y_valores

def graficar_resultados(t, y, titulo, etiquetas):
    S = y[:, 0]
    Z = y[:, 1]
    R = y[:, 2]
    
    vista = Vista(x_min=0, x_max=t[-1], y_min=0, y_max=np.max(y) * 1.1)
    g = Grafica(vista)
    g.cuadricula()
    
    if "S" in etiquetas:
        g.curva("S", t.tolist(), S.tolist(), label="S(t) - Susceptibles", color="blue")
    if "Z" in etiquetas:
        g.curva("Z", t.tolist(), Z.tolist(), label="Z(t) - Zombies", color="red")
    if "R" in etiquetas:
        g.curva("R", t.tolist(), R.tolist(), label="R(t) - Removidos", color="green")
        
    g._ax.legend()
    g._ax.set_title(titulo)
    g._ax.set_xlabel("Tiempo (días)")
    g._ax.set_ylabel("Población")
    

#parte1 rk4
print("*** Parte 1: Simulacion estandar (RK4) ***")

#parametros y condiciones iniciales
S0 = 999900.0
Z0 = 100.0
R0 = 0.0
y_inicial = np.array([S0, Z0, R0])

BETA = 0.000005
ALPHA = 0.000001
ZETA = 0.01
H = 0.1
T_FINAL = 365

# Define la función del modelo con los parámetros de la Parte 1
f_parte1 = lambda t, y: modelo_szr(t, y, beta=BETA, alpha=ALPHA, zeta=ZETA)

t1, y1 = simular_sistema(runge_kutta_orden_4, f_parte1, y_inicial, T_FINAL, H)

graficar_resultados(t1, y1, "*** Parte 1: Simulacion estandar (RK4) ***", ["S", "Z", "R"])

#valores finales 
S_fin = y1[-1, 0]
Z_fin = y1[-1, 1]
R_fin = y1[-1, 2]
print(f"\nValores finales en t={T_FINAL} dias:")
tabla_fin = Tabla("Poblacion", "Valor final")
print(tabla_fin.encabezado())
print(tabla_fin.fila("S(t)", S_fin))
print(tabla_fin.fila("Z(t)", Z_fin))
print(tabla_fin.fila("R(t)", R_fin))


# parte 2.1 convergencia
print("\n*** Ejecutando parte 2.1: Convergencia Euler vs RK4 ***")

pasos_h = [0.5, 5.0]
for h_paso in pasos_h:
    t_euler, y_euler = simular_sistema(euler, f_parte1, y_inicial, T_FINAL, h_paso)
    t_rk4, y_rk4 = simular_sistema(runge_kutta_orden_4, f_parte1, y_inicial, T_FINAL, h_paso)
     #Grafica.cerrar()

    #comparar gráficas Z(t)
    vista_z = Vista(0, T_FINAL, 0, np.max(y_inicial))

    g_z = Grafica(vista_z)
    g_z.cuadricula()
    g_z.curva("Z_Euler", t_euler.tolist(), y_euler[:, 1].tolist(), label=f"Z(t) Euler (h={h_paso})", linestyle="--")
    g_z.curva("Z_RK4", t_rk4.tolist(), y_rk4[:, 1].tolist(), label=f"Z(t) RK4 (h={h_paso})")
    g_z._ax.legend()
    g_z._ax.set_title(f"Parte 2.1: Comparacion Z(t) con h={h_paso}")
    g_z._ax.set_xlabel("Tiempo (días)")
    g_z._ax.set_ylabel("Población Zombie")

Grafica.mostrar()
print("Generando graficos....")
print("***Agregar reporte....***")


#parte 2.2 sensibilidad en guerra total
print("\n--- Ejecutando Parte 2.2: Escenario 'Guerra Total' (RK4) ---")

#nuevos parametros mejores
ALPHA_NUEVO = 0.00002
ZETA_NUEVO = 0.0

f_parte2 = lambda t, y: modelo_szr(t, y, beta=BETA, alpha=ALPHA_NUEVO, zeta=ZETA_NUEVO)


t2, y2 = simular_sistema(runge_kutta_orden_4, f_parte2, y_inicial, T_FINAL, H)


graficar_resultados(t2, y2, "Parte 2.2: Escenario de Guerra total (RK4, h=0.1)", ["S", "Z"])

print("Generando graficos.")
print("***falta reporte***.")

print("\nMostrando todos los gráficos...")
Grafica.mostrar()
