# Laboratorio 4: Sistema de Logística de Entregas con QuadTree

## 1. Propósito del Proyecto y Contexto

Este proyecto desarrolla un **sistema de optimización logística para entregas urbanas** en una ciudad modelada en un espacio bidimensional continuo de $10.000\text{ m} \times 10.000\text{ m}$ (10 km × 10 km).

El sistema administra las coordenadas $(x, y)$ de **10.000 puntos de entrega estáticos** y resuelve de manera eficiente dos problemas espaciales críticos:
1. **Búsqueda por Rango Circular (*Range Search*)**: ¿Qué puntos de entrega se encuentran dentro de un radio de **500 metros** de una ubicación dada?
2. **Vecino Más Cercano (*Nearest Neighbor - 1-NN y K-NN*)**: ¿Cuál es el punto de entrega más cercano a un repartidor o centro de distribución?

### Objetivo Principal
Implementar desde cero una estructura de datos espacial **QuadTree (PR-QuadTree)** sin depender de librerías externas (como `scipy.spatial` o árboles preconstruidos) y comparar su rendimiento frente al enfoque de **Fuerza Bruta** lineal.

---

## 2. Estructura de Archivos del Laboratorio

| Archivo | Rol y Contenido |
| :--- | :--- |
| **`Quadtree.py`** | Contiene la implementación pura desde cero de la estructura de datos: clases `Point`, `BoundingBox` y `QuadTree`, así como los algoritmos de partición espacial, búsqueda circular por radio, vecino más cercano y funciones de fuerza bruta para validación. |
| **`test.py`** | Suite de pruebas unitarias que indexa 10.000 puntos, valida la exactitud matemática contra fuerza bruta y genera las **gráficas de verificación visual** requeridas. |
| **`analisis.py`** | Módulo de evaluación de rendimiento comparativo. Mide tiempos de ejecución para diferentes tamaños de $N$ ($50$ a $10.000$), calcula la aceleración (*speedup*) y genera la gráfica comparativa de complejidad. |
| **`pseudocodigo.md`** | Especificación teórica y pseudocódigo formal de referencia. |

---

## 3. Arquitectura y Funcionamiento del QuadTree

El árbol implementado corresponde a un **PR-QuadTree (Point-Region QuadTree)**:
* **Partición Espacial Regular**: El espacio 2D se divide en 4 cuadrantes simétricos (**NW, NE, SW, SE**) usando el centro geométrico del área como punto de corte ($x_{\text{corte}} = cx, y_{\text{corte}} = cy$).
* **Almacenamiento Exclusivo en Hojas**: Cada nodo almacena hasta una capacidad fija (`capacity = 16`). Al desbordarse, el nodo se subdivide y redistribuye los puntos hacia los cuadrantes hijos, dejando los nodos internos como directores de tráfico espacial y las hojas como contenedores de datos.
* **Poda Geométrica (*Spatial Pruning*)**: 
  * En la búsqueda por radio de $500\text{ m}$, el método `intersects_circle` evalúa por *clamping* si el círculo de búsqueda colisiona con el rectángulo del nodo. Si no hay colisión, **se descarta todo el cuadrante y sus descendientes en $O(1)$**, evitando comparar miles de puntos lejanos.
  * Reduce la complejidad de búsqueda de $O(N)$ (fuerza bruta) a un promedio de **$O(\log N)$**.

---

## 4. Respuestas al Análisis Comparativo

### ¿Para qué tamaño de datos el QuadTree comienza a ser más rápido que la Fuerza Bruta?

* **Punto de cruce (*Crossover Point*)**: El QuadTree comienza a superar a la fuerza bruta a partir de **$N \approx 50 - 100$ puntos**.
* **Justificación técnica**:
  * Para $N < 50$, el recorrido de una lista contigua simple en Python tiene menos sobrecarga (*overhead*) que la creación y llamadas a métodos recursivos en el árbol.
  * Para $N \ge 100$, la poda de cuadrantes compensa ampliamente la sobrecarga de recursión.
  * Para los **10.000 puntos** requeridos por el laboratorio, el QuadTree realiza la búsqueda por radio en **$\approx 0.13\text{ ms}$** frente a **$2.36\text{ ms}$** de la fuerza bruta, logrando una **aceleración de $17.5\times$**.

### Costo Amortizado de Construcción
Construir el QuadTree con 10.000 puntos toma únicamente **$\approx 105\text{ ms}$**. Como los datos de entrega son **estáticos** (no cambian durante la operación), este costo se asume una sola vez al inicializar el sistema y se amortiza tras un puñado de consultas.

---

## 5. Salidas Visuales Generadas

Al ejecutar las pruebas se generan los siguientes artefactos de verificación a 300 DPI:

1. **`verificacion_radio.png`**: Representa la ciudad completa con los 10.000 puntos, la cuadrícula de partición del QuadTree, el círculo de $500\text{ m}$ de radio y los puntos capturados resaltados en rojo.
2. **`verificacion_vecino_cercano.png`**: Muestra la ubicación de consulta, la entrega más próxima (1-NN) y la "esfera vacía" que demuestra geométricamente la ausencia de puntos más cercanos.
3. **`verificacion_k_vecinos.png`**: Muestra los $K = 50$ vecinos más próximos conectados mediante rayos de proximidad y su frontera perimetral.
4. **`comparativa_rendimiento.png`**: Gráfica de curvas de tiempo de búsqueda (QuadTree vs Fuerza Bruta) destacando el punto de cruce y la diferencia de escala de complejidad.

---

## 6. Instrucciones de Ejecución

Para reproducir las pruebas y generar las visualizaciones:

```bash
# 1. Ejecutar pruebas unitarias y generación de gráficas visuales
python test.py

# 2. Ejecutar análisis comparativo de rendimiento y benchmark
python analisis.py
```
