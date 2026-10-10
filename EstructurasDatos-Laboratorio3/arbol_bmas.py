"""Implementación de árbol B+ y benchmark autónomo de búsqueda por ID."""

from dataclasses import dataclass, field
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
class NodoBMas:
    """Nodo B+: claves separadoras, hijos/valores y enlace entre hojas."""

    hoja: bool
    claves: list = field(default_factory=list)
    hijos: list = field(default_factory=list)
    siguiente: "NodoBMas | None" = None


def _posicion_izquierda(claves, valor):
    """Calcula con búsqueda binaria la primera posición >= al valor."""
    izquierda = 0
    derecha = len(claves)
    while izquierda < derecha:
        mitad = (izquierda + derecha) // 2
        if claves[mitad] < valor:
            izquierda = mitad + 1
        else:
            derecha = mitad
    return izquierda


def _posicion_derecha(claves, valor):
    """Calcula con búsqueda binaria la primera posición > al valor."""
    izquierda = 0
    derecha = len(claves)
    while izquierda < derecha:
        mitad = (izquierda + derecha) // 2
        if valor < claves[mitad]:
            derecha = mitad
        else:
            izquierda = mitad + 1
    return izquierda


class ArbolBMas:
    """Árbol balanceado que guarda registros en hojas enlazadas."""

    def __init__(self, max_claves=31):
        """Crea el árbol vacío y define el máximo de claves por nodo."""
        if max_claves < 3:
            raise ValueError("max_claves debe ser al menos 3")
        self.max_claves = max_claves
        self.raiz = NodoBMas(hoja=True)

    def insertar(self, estudiante):
        """Inserta por ID; crea una nueva raíz si la anterior se divide."""
        separador, nuevo_derecho = self._insertar_en_nodo(self.raiz, estudiante)
        if nuevo_derecho is not None:
            self.raiz = NodoBMas(
                hoja=False,
                claves=[separador],
                hijos=[self.raiz, nuevo_derecho],
            )

    def _insertar_en_nodo(self, nodo, estudiante):
        """Inserta recursivamente y propaga separadores cuando un nodo se divide."""
        if nodo.hoja:
            posicion = _posicion_izquierda(nodo.claves, estudiante.id)
            if posicion < len(nodo.claves) and nodo.claves[posicion] == estudiante.id:
                raise ValueError(f"Ya existe un estudiante con ID {estudiante.id}")
            nodo.claves.insert(posicion, estudiante.id)
            nodo.hijos.insert(posicion, estudiante)

            if len(nodo.claves) <= self.max_claves:
                return None, None

            mitad = len(nodo.claves) // 2
            nuevo_derecho = NodoBMas(
                hoja=True,
                claves=nodo.claves[mitad:],
                hijos=nodo.hijos[mitad:],
                siguiente=nodo.siguiente,
            )
            nodo.claves = nodo.claves[:mitad]
            nodo.hijos = nodo.hijos[:mitad]
            nodo.siguiente = nuevo_derecho
            return nuevo_derecho.claves[0], nuevo_derecho

        posicion = _posicion_derecha(nodo.claves, estudiante.id)
        separador, nuevo_derecho = self._insertar_en_nodo(nodo.hijos[posicion], estudiante)
        if nuevo_derecho is None:
            return None, None

        nodo.claves.insert(posicion, separador)
        nodo.hijos.insert(posicion + 1, nuevo_derecho)
        if len(nodo.claves) <= self.max_claves:
            return None, None

        mitad = len(nodo.claves) // 2
        separador_promovido = nodo.claves[mitad]
        nuevo_derecho = NodoBMas(
            hoja=False,
            claves=nodo.claves[mitad + 1:],
            hijos=nodo.hijos[mitad + 1:],
        )
        nodo.claves = nodo.claves[:mitad]
        nodo.hijos = nodo.hijos[:mitad + 1]
        return separador_promovido, nuevo_derecho

    def buscar_por_id(self, id):
        """Desciende a la hoja correspondiente y devuelve el estudiante o None."""
        actual = self.raiz
        while not actual.hoja:
            actual = actual.hijos[_posicion_derecha(actual.claves, id)]

        posicion = _posicion_izquierda(actual.claves, id)
        if posicion < len(actual.claves) and actual.claves[posicion] == id:
            return actual.hijos[posicion]
        return None

    def listar_ordenados(self):
        """Empieza en la hoja más izquierda y sigue sus enlaces en orden de ID."""
        actual = self.raiz
        while not actual.hoja:
            actual = actual.hijos[0]

        ordenados = []
        while actual is not None:
            ordenados.extend(actual.hijos)
            actual = actual.siguiente
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
    sistema = ArbolBMas()
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

    ruta_csv = Path(__file__).resolve().parent / f"tiempos_bmas_{escenario}.csv"
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

    print("Estructura: Árbol B+")
    print(f"Registros por escenario: {cantidad}")
    for escenario, dataset in datasets.items():
        print(f"Escenario: {escenario.capitalize()}")
        ejecutar_escenario(escenario, dataset)