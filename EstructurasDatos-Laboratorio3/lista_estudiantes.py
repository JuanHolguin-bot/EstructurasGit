"""Implementación de lista y benchmark autónomo de búsqueda lineal por ID."""

from dataclasses import dataclass
import csv
from pathlib import Path
import random
import statistics
import time


@dataclass
class Estudiante:
    """Registro del sistema con identificador, nombre y promedio académico."""

    id: int
    nombre: str
    promedio: float


class ListaEstudiantes:
    """Almacena estudiantes en orden de inserción y los busca linealmente."""

    def __init__(self):
        """Inicializa la lista vacía de registros."""
        self.estudiantes = []

    def insertar(self, estudiante):
        """Agrega al final; el conjunto de entrada debe tener ID únicos."""
        self.estudiantes.append(estudiante)

    def buscar_por_id(self, id):
        """Busca un estudiante recorriendo la lista desde el inicio."""
        for estudiante in self.estudiantes:
            if estudiante.id == id:
                return estudiante
        return None

    def listar_ordenados(self):
        """Devuelve una nueva lista de estudiantes ordenada por ID."""
        return sorted(self.estudiantes, key=lambda estudiante: estudiante.id)


def generar_estudiantes(cantidad, ids=None):
    """Genera estudiantes usando los ID recibidos o ID aleatorios únicos."""
    nombres = ["Ana", "Carlos", "Laura", "Mateo", "Sofia", "David"]
    apellidos = ["Garcia", "Lopez", "Martinez", "Perez", "Rodriguez"]
    if ids is None:
        ids = random.sample(range(1, cantidad * 100 + 1), cantidad)
    return [
        Estudiante(
            id=identificador,
            nombre=f"{random.choice(nombres)} {random.choice(apellidos)}",
            promedio=round(random.uniform(0.0, 5.0), 2),
        )
        for identificador in ids
    ]


def generar_datasets(cantidad):
    """Crea dos conjuntos del mismo tamaño: IDs consecutivos y únicos aleatorios."""
    ids_ordenados = range(1, cantidad + 1)
    ids_aleatorios = random.sample(range(1, cantidad * 100 + 1), cantidad)
    return {
        "ordenado": generar_estudiantes(cantidad, ids_ordenados),
        "aleatorio": generar_estudiantes(cantidad, ids_aleatorios),
    }


def ejecutar_escenario(escenario, dataset):
    """Mide inserción y 100 búsquedas, imprime estadísticas y exporta cada tiempo."""
    sistema = ListaEstudiantes()
    inicio = time.perf_counter()
    for estudiante in dataset:
        sistema.insertar(estudiante)
    tiempo_insercion = (time.perf_counter() - inicio) * 1_000

    ids_busqueda = random.sample([estudiante.id for estudiante in dataset], 100)
    mediciones = []
    for identificador in ids_busqueda:
        inicio = time.perf_counter()
        sistema.buscar_por_id(identificador)
        mediciones.append((time.perf_counter() - inicio) * 1_000)

    ruta_csv = Path(__file__).resolve().parent / f"tiempos_lista_{escenario}.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=["id_buscado", "tiempo_busqueda_ms"])
        escritor.writeheader()
        escritor.writerows(
            {"id_buscado": identificador, "tiempo_busqueda_ms": tiempo}
            for identificador, tiempo in zip(ids_busqueda, mediciones)
        )

    print(f"  Tiempo de inserción: {tiempo_insercion:.6f} ms")
    print(f"  Búsqueda promedio: {statistics.mean(mediciones):.6f} ms")
    print(f"  Búsqueda mínima: {min(mediciones):.6f} ms")
    print(f"  Búsqueda máxima: {max(mediciones):.6f} ms")
    print(f"  Desviación estándar: {statistics.stdev(mediciones):.6f} ms")
    print(f"  CSV: {ruta_csv.name}")


if __name__ == "__main__":
    # Esta prueba directa es independiente del benchmark de escalabilidad.
    cantidad = 10_000
    random.seed(42)
    datasets = generar_datasets(cantidad)

    print("Estructura: Lista (búsqueda lineal)")
    print(f"Registros por escenario: {cantidad}")
    for escenario, dataset in datasets.items():
        print(f"Escenario: {escenario.capitalize()}")
        ejecutar_escenario(escenario, dataset)