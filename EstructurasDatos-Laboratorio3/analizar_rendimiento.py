"""Analiza los seis CSV con memoria acotada y crea dos gráficas Plotly interactivas."""

import argparse
import csv
from dataclasses import dataclass
from math import sqrt
from pathlib import Path

import plotly.graph_objects as go


ARCHIVOS = (
    ("Lista", "Ordenada", "busquedas_ordenadas_lista.csv"),
    ("Lista", "Aleatoria", "busquedas_aleatorias_lista.csv"),
    ("ABB", "Ordenada", "busquedas_ordenadas_abb.csv"),
    ("ABB", "Aleatoria", "busquedas_aleatorias_abb.csv"),
    ("B+", "Ordenada", "busquedas_ordenadas_bmas.csv"),
    ("B+", "Aleatoria", "busquedas_aleatorias_bmas.csv"),
)
COLUMNAS_ESPERADAS = (
    "Tamano_N",
    "Tiempo_Insercion_Global_ms",
    "ID_Buscado",
    "Tiempo_Busqueda_ms",
)


@dataclass
class Acumulador:
    """Calcula media y desviación estándar muestral con memoria constante."""

    cantidad: int = 0
    media: float = 0.0
    suma_cuadrados: float = 0.0

    def agregar(self, valor):
        self.cantidad += 1
        diferencia = valor - self.media
        self.media += diferencia / self.cantidad
        diferencia_actualizada = valor - self.media
        self.suma_cuadrados += diferencia * diferencia_actualizada

    @property
    def desviacion_estandar(self):
        if self.cantidad < 2:
            return 0.0
        return sqrt(self.suma_cuadrados / (self.cantidad - 1))


def leer_estadisticas(ruta_csv):
    """Lee filas en streaming y calcula medias/desviaciones por métrica y tamaño."""
    acumuladores = {
        "Tiempo_Busqueda_ms": {},
        "Tiempo_Insercion_Global_ms": {},
    }

    with ruta_csv.open("r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        if tuple(lector.fieldnames or ()) != COLUMNAS_ESPERADAS:
            raise ValueError(
                f"Columnas inválidas en {ruta_csv.name}. "
                f"Se esperaban: {', '.join(COLUMNAS_ESPERADAS)}"
            )

        for numero_fila, fila in enumerate(lector, start=2):
            try:
                tamano = int(fila["Tamano_N"])
                tiempos_ms = {
                    columna: float(fila[columna])
                    for columna in acumuladores
                }
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Dato inválido en {ruta_csv.name}, fila {numero_fila}"
                ) from error

            for columna, tiempo_ms in tiempos_ms.items():
                if tiempo_ms <= 0:
                    raise ValueError(
                        f"{columna} debe ser positivo para la escala logarítmica: "
                        f"{ruta_csv.name}, fila {numero_fila}"
                    )
                acumuladores[columna].setdefault(tamano, Acumulador()).agregar(
                    tiempo_ms
                )

    return acumuladores


def crear_grafica(resultados, columna, ruta_html, tipo_tiempo, nombre_estructura):
    """Grafica exclusivamente medias en Y logarítmica y guarda un HTML autónomo."""
    estilos = {
        "Lista": {"color": "#1565C0", "marker": "circle"},
        "ABB": {"color": "#D84315", "marker": "square"},
        "B+": {"color": "#2E7D32", "marker": "triangle-up"},
    }
    lineas = {"Ordenada": "solid", "Aleatoria": "dash"}
    figura = go.Figure()

    for estructura, orden, por_tamano in resultados:
        tamanos = sorted(por_tamano[columna])
        promedios = [por_tamano[columna][tamano].media for tamano in tamanos]
        figura.add_trace(
            go.Scatter(
                x=tamanos,
                y=promedios,
                customdata=[format(promedio, ".17g") for promedio in promedios],
                mode="lines+markers",
                name=f"{nombre_estructura[estructura]} ({orden.lower()})",
                line={
                    "color": estilos[estructura]["color"],
                    "dash": lineas[orden],
                    "width": 2,
                },
                marker={"symbol": estilos[estructura]["marker"], "size": 8},
                hovertemplate=(
                    "Cantidad de registros (N): %{x:,.0f}<br>"
                    f"Tiempo promedio de {tipo_tiempo}: "
                    "%{customdata} ms"
                    "<extra>%{fullData.name}</extra>"
                ),
            )
        )

    figura.update_layout(
        title=f"Tiempo promedio de {tipo_tiempo} según estructura y tamaño",
        xaxis_title="Cantidad de registros (N)",
        yaxis_title=f"Tiempo promedio de {tipo_tiempo} (ms, escala logarítmica)",
        hovermode="closest",
        dragmode="pan",
        legend_title="Estructura y orden de entrada",
        template="plotly_white",
    )
    figura.update_yaxes(type="log")
    ruta_html.parent.mkdir(parents=True, exist_ok=True)
    figura.write_html(
        ruta_html,
        include_plotlyjs=True,
        full_html=True,
        config={"scrollZoom": True, "displaylogo": False, "responsive": True},
    )
    print(f"Gráfica interactiva guardada en: {ruta_html}")


def analizar(carpeta_csv, ruta_html, ruta_html_insercion):
    """Procesa los seis CSV, imprime estadísticas y genera gráficas de ambas métricas."""
    resultados = []
    print("Estadísticas de búsqueda (ms; desviación estándar muestral)")

    for estructura, orden, nombre_archivo in ARCHIVOS:
        ruta_csv = carpeta_csv / nombre_archivo
        if not ruta_csv.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

        estadisticas = leer_estadisticas(ruta_csv)
        if not estadisticas["Tiempo_Busqueda_ms"]:
            print(
                f"\nSin mediciones válidas para {estructura} - entrada "
                f"{orden.lower()}; consulte benchmark_errores.csv."
            )
            continue
        resultados.append((estructura, orden, estadisticas))

        print(f"\n{estructura} - entrada {orden.lower()} ({nombre_archivo})")
        print("N, búsquedas, media_ms, desviación_estándar_ms")
        for tamano, estadistica in sorted(
            estadisticas["Tiempo_Busqueda_ms"].items()
        ):
            print(
                f"{tamano}, {estadistica.cantidad}, "
                f"{estadistica.media:.9g}, "
                f"{estadistica.desviacion_estandar:.9g}"
            )

    crear_grafica(
        resultados,
        "Tiempo_Busqueda_ms",
        ruta_html,
        "búsqueda",
        {"Lista": "Lista", "ABB": "ABB", "B+": "B+"},
    )
    crear_grafica(
        resultados,
        "Tiempo_Insercion_Global_ms",
        ruta_html_insercion,
        "inserción",
        {"Lista": "Lista", "ABB": "Árbol ABB", "B+": "Árbol B+"},
    )


def main():
    """Interpreta rutas opcionales de CSV y salidas HTML desde la línea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Analiza los CSV de rendimiento y genera gráficas HTML interactivas "
            "de las medias de búsqueda e inserción."
        )
    )
    carpeta_predeterminada = Path(__file__).resolve().parent
    parser.add_argument(
        "--csv-dir",
        type=Path,
        default=carpeta_predeterminada,
        help="Carpeta que contiene los seis CSV (por defecto, la carpeta del script).",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=carpeta_predeterminada / "grafico_rendimiento_interactivo.html",
        help="Ruta de salida para la gráfica HTML de búsqueda.",
    )
    parser.add_argument(
        "--salida-insercion",
        type=Path,
        default=carpeta_predeterminada / "grafico_insercion_interactivo.html",
        help="Ruta de salida para la gráfica HTML de inserción.",
    )
    argumentos = parser.parse_args()
    analizar(
        argumentos.csv_dir,
        argumentos.salida,
        argumentos.salida_insercion,
    )


if __name__ == "__main__":
    # Permite ejecutar el analizador como programa, además de importarlo como módulo.
    main()