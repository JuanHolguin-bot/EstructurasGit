"""Implementación iterativa de ABB y benchmark autónomo de búsqueda por ID."""

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


@dataclass
class Nodo:
    """Nodo ABB: guarda un estudiante y referencias a sus dos subárboles."""

    estudiante: Estudiante
    izquierdo: "Nodo | None" = None
    derecho: "Nodo | None" = None


class ArbolBinarioBusqueda:
    """ABB no balanceado cuya ruta depende del orden de inserción de los IDs."""

    def __init__(self):
        """Inicializa un árbol sin raíz."""
        self.raiz = None

    def insertar(self, estudiante):
        """Inserta iterativamente según el ID y rechaza identificadores duplicados."""
        nuevo = Nodo(estudiante)
        if self.raiz is None:
            self.raiz = nuevo
            return

        actual = self.raiz
        while True:
            if estudiante.id == actual.estudiante.id:
                raise ValueError(f"Ya existe un estudiante con ID {estudiante.id}")
            if estudiante.id < actual.estudiante.id:
                if actual.izquierdo is None:
                    actual.izquierdo = nuevo
                    return
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = nuevo
                    return
                actual = actual.derecho

    def buscar_por_id(self, id):
        """Busca iterativamente; devuelve el estudiante o None si no existe."""
        actual = self.raiz
        while actual is not None:
            if id == actual.estudiante.id:
                return actual.estudiante
            actual = actual.izquierdo if id < actual.estudiante.id else actual.derecho
        return None

    def listar_ordenados(self):
        """Devuelve los estudiantes por ID ascendente mediante recorrido inorden."""
        ordenados = []
        pendientes = []
        actual = self.raiz

        while actual is not None or pendientes:
            while actual is not None:
                pendientes.append(actual)
                actual = actual.izquierdo
            actual = pendientes.pop()
            ordenados.append(actual.estudiante)
            actual = actual.derecho

        return ordenados


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
    """Crea datasets ordenado y aleatorio con la misma cantidad de registros."""
    ids_ordenados = range(1, cantidad + 1)
    ids_aleatorios = random.sample(range(1, cantidad * 100 + 1), cantidad)
    return {
        "ordenado": generar_estudiantes(cantidad, ids_ordenados),
        "aleatorio": generar_estudiantes(cantidad, ids_aleatorios),
    }


def ejecutar_escenario(escenario, dataset):
    """Mide inserción y 100 búsquedas, imprime estadísticas y exporta cada tiempo."""
    sistema = ArbolBinarioBusqueda()
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

    ruta_csv = Path(__file__).resolve().parent / f"tiempos_abb_{escenario}.csv"
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

    print("Estructura: Árbol Binario de Búsqueda (ABB)")
    print(f"Registros por escenario: {cantidad}")
    for escenario, dataset in datasets.items():
        print(f"Escenario: {escenario.capitalize()}")
        ejecutar_escenario(escenario, dataset)