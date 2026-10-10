"""Ejecuta el benchmark secuencial y exporta mediciones separadas por estructura."""

import csv
from contextlib import ExitStack
from math import gcd
from pathlib import Path
import random
import time

from abb_estudiantes import ArbolBinarioBusqueda, Estudiante
from arbol_bmas import ArbolBMas
from lista_estudiantes import ListaEstudiantes


# Mantener los tamaños en orden facilita comparar el crecimiento de cada estructura.
TAMANOS = (100, 500, 1_000, 2_500, 5_000, 10_000, 25_000, 50_000, 100_000)
CANTIDAD_BUSQUEDAS = 100
ESTRUCTURAS = (
    ("lista", "Lista", ListaEstudiantes),
    ("abb", "ABB", ArbolBinarioBusqueda),
    ("bmas", "B+", ArbolBMas),
)
COLUMNAS_CSV = (
    "Tamano_N",
    "Tiempo_Insercion_Global_ms",
    "ID_Buscado",
    "Tiempo_Busqueda_ms",
)


def generar_dataset(tamano, tipo_orden):
    """Genera registros con IDs consecutivos o una permutación aleatoria reproducible."""
    if tipo_orden == "Ordenado":
        ids = range(1, tamano + 1)
    else:
        generador = random.Random(42 + tamano)
        multiplicador = 1 if tamano == 1 else generador.randrange(1, tamano)
        while gcd(multiplicador, tamano) != 1:
            multiplicador = generador.randrange(1, tamano)
        desplazamiento = generador.randrange(tamano)
        ids = (
            (multiplicador * posicion + desplazamiento) % tamano + 1
            for posicion in range(tamano)
        )

    return (
        Estudiante(id=identificador, nombre="Estudiante", promedio=4.0)
        for identificador in ids
    )


def liberar_estructura(sistema):
    """Desconecta iterativamente las referencias de la estructura para liberar memoria."""
    if isinstance(sistema, ListaEstudiantes):
        sistema.estudiantes.clear()
    elif isinstance(sistema, ArbolBinarioBusqueda):
        pendientes = [sistema.raiz] if sistema.raiz is not None else []
        while pendientes:
            nodo = pendientes.pop()
            if nodo.izquierdo is not None:
                pendientes.append(nodo.izquierdo)
            if nodo.derecho is not None:
                pendientes.append(nodo.derecho)
            nodo.izquierdo = None
            nodo.derecho = None
            nodo.estudiante = None
        sistema.raiz = None
    elif isinstance(sistema, ArbolBMas):
        pendientes = [sistema.raiz]
        while pendientes:
            nodo = pendientes.pop()
            if not nodo.hoja:
                pendientes.extend(nodo.hijos)
            nodo.siguiente = None
            nodo.claves.clear()
            nodo.hijos.clear()
        sistema.raiz = None


def medir_estructura(nombre, clase_sistema, estudiantes, ids_busqueda):
    """Cronometra inserción total y cada búsqueda; libera la estructura incluso si falla."""
    sistema = clase_sistema()

    try:
        inicio = time.perf_counter()
        for estudiante in estudiantes:
            sistema.insertar(estudiante)
        tiempo_insercion = (time.perf_counter() - inicio) * 1_000

        tiempos_busqueda = []
        for identificador in ids_busqueda:
            inicio = time.perf_counter()
            resultado = sistema.buscar_por_id(identificador)
            tiempos_busqueda.append((time.perf_counter() - inicio) * 1_000)
            if resultado is None:
                raise RuntimeError(f"{nombre} no encontró el ID {identificador}")

        if len(ids_busqueda) != CANTIDAD_BUSQUEDAS:
            raise ValueError(f"Se esperaban {CANTIDAD_BUSQUEDAS} IDs de búsqueda")
    finally:
        liberar_estructura(sistema)
    return tiempo_insercion, tiempos_busqueda


def ejecutar_benchmark():
    """Prueba tamaños, órdenes y estructuras; exporta seis CSV y un reporte de errores."""
    random.seed(42)
    carpeta_salida = Path(__file__).resolve().parent
    sufijos_orden = {
        "Ordenado": "ordenadas",
        "Aleatorio": "aleatorias",
    }
    errores = []

    with ExitStack() as archivos_abiertos:
        salidas = {}
        # Se crean los seis archivos al inicio; esta corrida reemplaza sus resultados previos.
        for tipo_orden, sufijo in sufijos_orden.items():
            for slug_estructura, nombre, _ in ESTRUCTURAS:
                ruta_csv = carpeta_salida / f"busquedas_{sufijo}_{slug_estructura}.csv"
                archivo = archivos_abiertos.enter_context(
                    ruta_csv.open("w", newline="", encoding="utf-8")
                )
                escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_CSV)
                escritor.writeheader()
                salidas[(nombre, tipo_orden)] = (escritor, archivo, ruta_csv)

        for _, nombre, clase_sistema in ESTRUCTURAS:
            # Terminar una estructura completa antes de pasar a la siguiente limita coexistencia.
            print(f"\nIniciando estructura: {nombre}")
            for tamano in TAMANOS:
                for tipo_orden in ("Ordenado", "Aleatorio"):
                    ids_busqueda = random.sample(
                        range(1, tamano + 1),
                        CANTIDAD_BUSQUEDAS,
                    )
                    estudiantes = generar_dataset(tamano, tipo_orden)
                    # La lista permite reutilizar la misma entrada en un escenario de medición.
                    estudiantes = list(estudiantes)
                    try:
                        tiempo_insercion, tiempos_busqueda = medir_estructura(
                            nombre,
                            clase_sistema,
                            estudiantes,
                            ids_busqueda,
                        )
                    except RecursionError as error:
                        errores.append(
                            {
                                "Estructura": nombre,
                                "Orden_Entrada": tipo_orden,
                                "Tamano_N": tamano,
                                "Tipo_Error": type(error).__name__,
                                "Mensaje": str(error),
                            }
                        )
                        print(
                            f"FALLO registrado | N = {tamano:,} | {tipo_orden} | "
                            f"{nombre} | {type(error).__name__}: {error}"
                        )
                        del estudiantes
                        continue

                    escritor, archivo, ruta_csv = salidas[(nombre, tipo_orden)]
                    escritor.writerows(
                        # Una fila por búsqueda; el tiempo total de inserción acompaña cada una.
                        {
                            "Tamano_N": tamano,
                            "Tiempo_Insercion_Global_ms": tiempo_insercion,
                            "ID_Buscado": identificador,
                            "Tiempo_Busqueda_ms": tiempo_busqueda,
                        }
                        for identificador, tiempo_busqueda in zip(
                            ids_busqueda,
                            tiempos_busqueda,
                        )
                    )
                    archivo.flush()
                    print(
                        f"Completado N = {tamano:,} | {tipo_orden} | {nombre} | "
                        f"inserción: {tiempo_insercion:.3f} ms | CSV: {ruta_csv.name}"
                    )
                    del estudiantes

    ruta_errores = carpeta_salida / "benchmark_errores.csv"
    with ruta_errores.open("w", newline="", encoding="utf-8") as archivo:
        columnas = (
            "Estructura",
            "Orden_Entrada",
            "Tamano_N",
            "Tipo_Error",
            "Mensaje",
        )
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(errores)

    print(f"\nReporte de errores guardado en: {ruta_errores}")
    print(f"Escenarios fallidos por recursión: {len(errores)}")
    print(f"\nSeis archivos CSV guardados en: {carpeta_salida}")


if __name__ == "__main__":
    # Punto de entrada del benchmark de escalabilidad completo.
    ejecutar_benchmark()