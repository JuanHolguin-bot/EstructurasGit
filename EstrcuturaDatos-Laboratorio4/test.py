import os
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from Quadtree import Point, BoundingBox, QuadTree, brute_force_radius, brute_force_nearest_neighbor

# =====================================================================
# MÓDULO DE VISUALIZACIÓN ORIGINAL PARA EL LABORATORIO
# =====================================================================

def dibujar_particiones_arbol(ax, nodo, color="#cccccc", grosor=0.6):
    """
    Función recursiva para graficar las líneas de corte de los cuadrantes
    del Quadtree, demostrando visualmente la partición espacial.
    """
    if nodo.divided:
        cx, cy = nodo.boundary.center_x, nodo.boundary.center_y
        hw, hh = nodo.boundary.half_width, nodo.boundary.half_height
        
        # Cruz que divide el nodo actual
        ax.plot([cx - hw, cx + hw], [cy, cy], color=color, linewidth=grosor, linestyle='-', alpha=0.5)
        ax.plot([cx, cx], [cy - hh, cy + hh], color=color, linewidth=grosor, linestyle='-', alpha=0.5)

        # Recursión a los cuatro hijos
        dibujar_particiones_arbol(ax, nodo.north_west, color, grosor * 0.8)
        dibujar_particiones_arbol(ax, nodo.north_east, color, grosor * 0.8)
        dibujar_particiones_arbol(ax, nodo.south_west, color, grosor * 0.8)
        dibujar_particiones_arbol(ax, nodo.south_east, color, grosor * 0.8)


def graficar_cobertura_radio(puntos, encontrados, origen, radio, arbol=None, destino="verificacion_radio.png"):
    """
    Visualiza la búsqueda por rango circular (500m).
    Muestra el área de cobertura sombreada y destaca las entregas alcanzadas.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Opcional: mostrar las divisiones de los cuadrantes del QuadTree de fondo
    if arbol is not None:
        dibujar_particiones_arbol(ax, arbol)

    # 1. Conjunto general de entregas (fondo)
    px = [p.x for p in puntos]
    py = [p.y for p in puntos]
    ax.scatter(px, py, s=1.5, color='#94a3b8', alpha=0.35, label='Entregas en la ciudad')

    # 2. Círculo que representa el rango de cobertura con relleno traslúcido
    area_cobertura = Circle(
        (origen.x, origen.y),
        radio,
        facecolor='#38bdf8',
        edgecolor='#0284c7',
        linewidth=1.8,
        linestyle='--',
        alpha=0.25,
        label=f'Radio de cobertura ({int(radio)} m)'
    )
    ax.add_patch(area_cobertura)

    # 3. Puntos capturados dentro del radio
    if encontrados:
        ex = [p.x for p in encontrados]
        ey = [p.y for p in encontrados]
        ax.scatter(ex, ey, s=14, color='#e11d48', edgecolors='#881337', linewidth=0.5, zorder=4, label=f'Entregas cubiertas ({len(encontrados)})')

    # 4. Ubicación de consulta
    ax.scatter([origen.x], [origen.y], s=90, color='#0f172a', marker='P', edgecolors='white', linewidth=1.2, zorder=5, label='Punto de consulta')

    # Configuración de ejes y estética
    ax.set_title("Verificación: Búsqueda Espacial por Radio de Entrega", fontsize=13, fontweight='bold', pad=14)
    ax.set_xlabel("Distancia horizontal X (metros)", fontsize=10)
    ax.set_ylabel("Distancia vertical Y (metros)", fontsize=10)
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 10000)
    ax.set_aspect('equal')
    ax.grid(True, color='#e2e8f0', linestyle=':')
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(destino, dpi=300)
    plt.close(fig)
    print(f"✓ Guardada: {destino}")


def graficar_par_mas_cercano(puntos, origen, mas_cercano, destino="verificacion_vecino_cercano.png"):
    """
    Visualiza el vecino más cercano (1-NN).
    Dibuja la 'esfera vacía': un círculo de radio igual a la distancia mínima,
    demostrando geométricamente que no existe ninguna otra entrega más próxima.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    distancia = origen.distance_to(mas_cercano)

    # 1. Puntos de fondo
    ax.scatter([p.x for p in puntos], [p.y for p in puntos], s=1.5, color='#94a3b8', alpha=0.35, label='Entregas')

    # 2. Círculo vacío delimitador (prueba visual de vecindad mínima)
    esfera_vacia = Circle(
        (origen.x, origen.y),
        distancia,
        facecolor='#22c55e',
        edgecolor='#15803d',
        linewidth=1.4,
        linestyle=':',
        alpha=0.15,
        label=f'Radio mínimo ({distancia:.1f} m)'
    )
    ax.add_patch(esfera_vacia)

    # 3. Vector de conexión entre consulta y vecino
    ax.annotate(
        "",
        xy=(mas_cercano.x, mas_cercano.y),
        xytext=(origen.x, origen.y),
        arrowprops=dict(arrowstyle="->", color="#15803d", lw=1.8, ls="-")
    )

    # 4. Puntos destacados
    ax.scatter([origen.x], [origen.y], s=90, color='#0f172a', marker='P', edgecolors='white', linewidth=1.2, zorder=5, label='Consulta')
    ax.scatter([mas_cercano.x], [mas_cercano.y], s=70, color='#16a34a', marker='o', edgecolors='white', linewidth=1.2, zorder=6, label=f'Entrega más cercana ({distancia:.1f}m)')

    # Texto con la métrica
    punto_medio_x = (origen.x + mas_cercano.x) / 2
    punto_medio_y = (origen.y + mas_cercano.y) / 2
    ax.text(punto_medio_x + 80, punto_medio_y + 80, f"d = {distancia:.2f} m", color='#14532d', fontsize=9, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#86efac", alpha=0.85))

    # Configuración de ejes
    ax.set_title("Verificación: Punto de Entrega Más Cercano (1-NN)", fontsize=13, fontweight='bold', pad=14)
    ax.set_xlabel("Coordenada X (metros)", fontsize=10)
    ax.set_ylabel("Coordenada Y (metros)", fontsize=10)
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 10000)
    ax.set_aspect('equal')
    ax.grid(True, color='#e2e8f0', linestyle=':')
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(destino, dpi=300)
    plt.close(fig)
    print(f"✓ Guardada: {destino}")


def graficar_grupo_k_vecinos(puntos, origen, vecinos, k_total, destino="verificacion_k_vecinos.png"):
    """
    Visualiza los K vecinos más cercanos conectando cada punto seleccionado
    mediante trazos de proximidad.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # 1. Puntos de fondo
    ax.scatter([p.x for p in puntos], [p.y for p in puntos], s=1.5, color='#94a3b8', alpha=0.35, label='Entregas')

    # 2. Conexiones a los K vecinos
    dist_max = 0.0
    for i, v in enumerate(vecinos):
        d = origen.distance_to(v)
        if d > dist_max:
            dist_max = d
        ax.plot([origen.x, v.x], [origen.y, v.y], color='#f97316', linestyle='--', linewidth=0.9, alpha=0.6)

    # 3. Círculo contenedor de los K vecinos
    frontera_k = Circle(
        (origen.x, origen.y),
        dist_max,
        fill=False,
        edgecolor='#ea580c',
        linewidth=1.2,
        linestyle='-.',
        label=f'Frontera K={k_total} ({dist_max:.1f} m)'
    )
    ax.add_patch(frontera_k)

    # 4. Puntos de los K vecinos y origen
    vx = [v.x for v in vecinos]
    vy = [v.y for v in vecinos]
    ax.scatter(vx, vy, s=18, color='#f97316', edgecolors='#9a3412', linewidth=0.6, zorder=5, label=f'{k_total} Vecinos seleccionados')
    ax.scatter([origen.x], [origen.y], s=90, color='#0f172a', marker='P', edgecolors='white', linewidth=1.2, zorder=6, label='Consulta')

    # Configuración de ejes
    ax.set_title(f"Verificación: Conjunto de {k_total} Vecinos Más Próximos", fontsize=13, fontweight='bold', pad=14)
    ax.set_xlabel("Coordenada X (metros)", fontsize=10)
    ax.set_ylabel("Coordenada Y (metros)", fontsize=10)
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 10000)
    ax.set_aspect('equal')
    ax.grid(True, color='#e2e8f0', linestyle=':')
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(destino, dpi=300)
    plt.close(fig)
    print(f"✓ Guardada: {destino}")


# =====================================================================
# EJECUCIÓN DE PRUEBAS Y GENERACIÓN DE SALIDAS
# =====================================================================
if __name__ == "__main__":
    random.seed(42)
    ESPACIO = 10000.0
    CANTIDAD_ENTREGAS = 10000
    CAPACIDAD = 16
    DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

    print("==================================================")
    print(" LABORATORIO 4: SISTEMA DE LOGÍSTICA CON QUADTREE ")
    print("==================================================")

    # 1. Definición del marco geográfico
    marco = BoundingBox(
        center_x=ESPACIO / 2.0,
        center_y=ESPACIO / 2.0,
        half_width=ESPACIO / 2.0,
        half_height=ESPACIO / 2.0
    )

    print(f"\n[1] Creando {CANTIDAD_ENTREGAS} puntos de entrega...")
    entregas = [
        Point(random.uniform(0, ESPACIO), random.uniform(0, ESPACIO), data=f"ENV-{i:05d}")
        for i in range(CANTIDAD_ENTREGAS)
    ]

    print("[2] Insertando en el QuadTree...")
    arbol = QuadTree(marco, capacity=CAPACIDAD)
    for punto in entregas:
        arbol.insert(punto)
    print(f"    QuadTree listo con {len(arbol.get_all_points())} elementos indexados.")

    # 2. Pruebas y consultas espaciales
    consulta = Point(5000.0, 5000.0)
    radio_busqueda = 500.0

    print("\n[3] Ejecutando consultas y comparando con fuerza bruta:")

    # Consulta A: Puntos a 500m
    resultado_radio = arbol.query_radius(consulta, radio_busqueda)
    esperado_radio = brute_force_radius(entregas, consulta, radio_busqueda)
    assert len(resultado_radio) == len(esperado_radio)
    assert set(p.data for p in resultado_radio) == set(p.data for p in esperado_radio)
    print(f"    • Radio 500m: {len(resultado_radio)} entregas detectadas (coincidencia perfecta).")

    # Consulta B: Vecino más cercano
    mas_cercano = arbol.nearest_neighbor(consulta)
    esperado_cercano = brute_force_nearest_neighbor(entregas, consulta)
    assert abs(consulta.distance_to(mas_cercano) - consulta.distance_to(esperado_cercano)) < 1e-6
    print(f"    • Vecino más próximo: {mas_cercano.data} a {consulta.distance_to(mas_cercano):.2f} metros (coincidencia perfecta).")

    # Consulta C: K vecinos (K=50)
    K = 50
    k_proximos = arbol.k_nearest_neighbors(consulta, k=K)
    print(f"    • {K} vecinos más próximos identificados.")

    # 3. Generación de las gráficas
    print("\n[4] Generando gráficas de verificación visual...")
    graficar_cobertura_radio(
        entregas,
        resultado_radio,
        consulta,
        radio_busqueda,
        arbol=arbol,
        destino=os.path.join(DIRECTORIO_BASE, "verificacion_radio.png")
    )

    graficar_par_mas_cercano(
        entregas,
        consulta,
        mas_cercano,
        destino=os.path.join(DIRECTORIO_BASE, "verificacion_vecino_cercano.png")
    )

    graficar_grupo_k_vecinos(
        entregas,
        consulta,
        k_proximos,
        k_total=K,
        destino=os.path.join(DIRECTORIO_BASE, "verificacion_k_vecinos.png")
    )

    print("\n✓ Todas las pruebas y visualizaciones concluyeron con éxito.")

