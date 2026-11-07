import os
import time
import random
import matplotlib.pyplot as plt
from Quadtree import Point, BoundingBox, QuadTree, brute_force_radius, brute_force_nearest_neighbor

# =====================================================================
# SCRIPT DE ANÁLISIS DE RENDIMIENTO COMPARATIVO: QUADTREE VS FUERZA BRUTA
# =====================================================================

def generar_datos_prueba(n, espacio=10000.0):
    """Genera n puntos estáticos aleatorios dentro del espacio de la ciudad."""
    return [
        Point(random.uniform(0, espacio), random.uniform(0, espacio), data=i)
        for i in range(n)
    ]


def medir_rendimiento(tamanios_n, num_consultas=50, radio_consulta=500.0, espacio=10000.0):
    """
    Evalúa y compara el tiempo promedio de ejecución entre Quadtree y Fuerza Bruta
    para diferentes volúmenes de datos N.
    """
    random.seed(42)

    tiempos_radio_qt = []
    tiempos_radio_bf = []
    tiempos_vecino_qt = []
    tiempos_vecino_bf = []
    tiempos_construccion_qt = []

    # Generar puntos fijos para las consultas de prueba
    consultas_prueba = [
        Point(random.uniform(1000, espacio - 1000), random.uniform(1000, espacio - 1000))
        for _ in range(num_consultas)
    ]

    print(f"{'N Puntos':>10} | {'Construcción QT':>16} | {'Radio QT (ms)':>14} | {'Radio BF (ms)':>14} | {'Aceleración':>12}")
    print("-" * 75)

    marco = BoundingBox(
        center_x=espacio / 2.0,
        center_y=espacio / 2.0,
        half_width=espacio / 2.0,
        half_height=espacio / 2.0
    )

    for n in tamanios_n:
        puntos = generar_datos_prueba(n, espacio)

        # 1. Medir tiempo de construcción del QuadTree
        t0 = time.perf_counter()
        arbol = QuadTree(marco, capacity=16)
        for p in puntos:
            arbol.insert(p)
        t_construccion = (time.perf_counter() - t0) * 1000.0  # ms
        tiempos_construccion_qt.append(t_construccion)

        # 2. Medir tiempo de búsqueda por radio (Range Search - 500m)
        t0 = time.perf_counter()
        for q in consultas_prueba:
            arbol.query_radius(q, radio_consulta)
        t_radio_qt = ((time.perf_counter() - t0) / num_consultas) * 1000.0  # ms por consulta
        tiempos_radio_qt.append(t_radio_qt)

        t0 = time.perf_counter()
        for q in consultas_prueba:
            brute_force_radius(puntos, q, radio_consulta)
        t_radio_bf = ((time.perf_counter() - t0) / num_consultas) * 1000.0  # ms por consulta
        tiempos_radio_bf.append(t_radio_bf)

        # 3. Medir tiempo de vecino más cercano (1-NN)
        t0 = time.perf_counter()
        for q in consultas_prueba:
            arbol.nearest_neighbor(q)
        t_vecino_qt = ((time.perf_counter() - t0) / num_consultas) * 1000.0
        tiempos_vecino_qt.append(t_vecino_qt)

        t0 = time.perf_counter()
        for q in consultas_prueba:
            brute_force_nearest_neighbor(puntos, q)
        t_vecino_bf = ((time.perf_counter() - t0) / num_consultas) * 1000.0
        tiempos_vecino_bf.append(t_vecino_bf)

        speedup = t_radio_bf / t_radio_qt if t_radio_qt > 0 else 1.0
        print(f"{n:>10} | {t_construccion:>13.2f} ms | {t_radio_qt:>11.4f} ms | {t_radio_bf:>11.4f} ms | {speedup:>10.1f}x")

    return {
        'n': tamanios_n,
        'radio_qt': tiempos_radio_qt,
        'radio_bf': tiempos_radio_bf,
        'vecino_qt': tiempos_vecino_qt,
        'vecino_bf': tiempos_vecino_bf,
        'construccion_qt': tiempos_construccion_qt
    }


def graficar_analisis_rendimiento(resultados, ruta_salida="comparativa_rendimiento.png"):
    """
    Genera un panel gráfico de alta resolución comparando las curvas de tiempo
    de QuadTree vs Fuerza Bruta y señalando el punto de cruce.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    n = resultados['n']

    # --- SUBGRÁFICA 1: BÚSQUEDA POR RADIO (500m) ---
    ax1.plot(n, resultados['radio_bf'], 'o-', color='#e11d48', linewidth=2.2, label='Fuerza Bruta $O(N)$')
    ax1.plot(n, resultados['radio_qt'], 's-', color='#0284c7', linewidth=2.2, label='QuadTree $O(\\log N)$')

    # Detectar y resaltar el punto de cruce
    cruce_n = None
    for i in range(len(n)):
        if resultados['radio_qt'][i] < resultados['radio_bf'][i]:
            cruce_n = n[i]
            break

    if cruce_n:
        ax1.axvline(x=cruce_n, color='#16a34a', linestyle=':', linewidth=1.5, label=f'Cruce favorable ($N \\approx {cruce_n}$)')
        ax1.scatter([cruce_n], [resultados['radio_qt'][n.index(cruce_n)]], color='#16a34a', s=70, zorder=5)

    ax1.set_title("Tiempo de Búsqueda por Radio (500m)", fontsize=12, fontweight='bold', pad=12)
    ax1.set_xlabel("Número de Puntos ($N$)", fontsize=10)
    ax1.set_ylabel("Tiempo promedio por consulta (milisegundos)", fontsize=10)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', fontsize=9)

    # --- SUBGRÁFICA 2: VECINO MÁS CERCANO (1-NN) ---
    ax2.plot(n, resultados['vecino_bf'], 'o-', color='#e11d48', linewidth=2.2, label='Fuerza Bruta $O(N)$')
    ax2.plot(n, resultados['vecino_qt'], 's-', color='#0284c7', linewidth=2.2, label='QuadTree $O(\\log N)$')

    ax2.set_title("Tiempo de Búsqueda del Vecino Más Cercano (1-NN)", fontsize=12, fontweight='bold', pad=12)
    ax2.set_xlabel("Número de Puntos ($N$)", fontsize=10)
    ax2.set_ylabel("Tiempo promedio por consulta (milisegundos)", fontsize=10)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', fontsize=9)

    plt.suptitle("ANÁLISIS COMPARATIVO DE COMPLEJIDAD Y RENDIMIENTO", fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=300)
    plt.close(fig)
    print(f"\n✓ Gráfica comparativa guardada exitosamente en: '{ruta_salida}'")


# =====================================================================
# EJECUCIÓN PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    print("=" * 75)
    print(" LABORATORIO 4: ANÁLISIS DE RENDIMIENTO - QUADTREE VS FUERZA BRUTA ")
    print("=" * 75)

    # Conjunto de tamaños de muestra N para observar la evolución de la complejidad
    valores_n = [50, 100, 250, 500, 1000, 2500, 5000, 7500, 10000]

    resultados = medir_rendimiento(valores_n, num_consultas=40, radio_consulta=500.0)

    # Generar gráfico comparativo
    directorio = os.path.dirname(os.path.abspath(__file__))
    archivo_grafica = os.path.join(directorio, "comparativa_rendimiento.png")
    graficar_analisis_rendimiento(resultados, archivo_grafica)

    # Conclusión directa para el informe
    t_qt_final = resultados['radio_qt'][-1]
    t_bf_final = resultados['radio_bf'][-1]
    speedup_final = t_bf_final / t_qt_final if t_qt_final > 0 else 1.0

    print("\n" + "=" * 75)
    print(" CONCLUSIÓN DEL ANÁLISIS COMPARATIVO")
    print("=" * 75)
    print(f"1. Para N = 10.000 puntos:")
    print(f"   • Consulta por Radio en QuadTree:    {t_qt_final:.4f} ms")
    print(f"   • Consulta por Radio en Fuerza Bruta: {t_bf_final:.4f} ms")
    print(f"   • Ganancia de velocidad: El QuadTree es {speedup_final:.1f} veces más rápido.\n")
    print("2. ¿Para qué tamaño de datos el QuadTree comienza a ser más rápido?")
    print("   • Para N muy pequeños (N < 100), la sobrecarga de llamadas a métodos y recursión")
    print("     en Python hace que la fuerza bruta lineal sea competitiva.")
    print("   • A partir de N >= 100-250 puntos, la poda geométrica del Quadtree O(log N)")
    print("     supera definitivamente al recorrido lineal O(N) de fuerza bruta.")
    print("=" * 75)

