import math


class Point:
    """
    Representa un punto en el plano bidimensional con coordenadas (x, y).
    Opcionalmente puede almacenar datos asociados (como ID de entrega o información de cliente).
    """
    def __init__(self, x, y, data=None):
        self.x = float(x)
        self.y = float(y)
        self.data = data

    def distance_to(self, other):
        """Calcula la distancia euclidiana hacia otro punto."""
        return math.hypot(self.x - other.x, self.y - other.y)

    dist = distance_to

    def __repr__(self):
        if self.data is not None:
            return f"Point({self.x}, {self.y}, data={self.data})"
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False


Punto = Point
XY = Point


class BoundingBox:
    """
    Caja delimitadora rectangular (AABB) definida por su centro (center_x, center_y)
    y sus semidimensiones (half_width, half_height).
    """
    def __init__(self, center_x, center_y, half_width, half_height):
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.half_width = float(half_width)
        self.half_height = float(half_height)

        self.x = self.center_x
        self.y = self.center_y
        self.w = self.half_width
        self.h = self.half_height

    @property
    def x_min(self):
        return self.center_x - self.half_width

    @property
    def x_max(self):
        return self.center_x + self.half_width

    @property
    def y_min(self):
        return self.center_y - self.half_height

    @property
    def y_max(self):
        return self.center_y + self.half_height

    def contains(self, point):
        """Verifica si un punto se encuentra dentro de esta caja."""
        return (
            self.x_min <= point.x <= self.x_max and
            self.y_min <= point.y <= self.y_max
        )

    def intersects_circle(self, center_x, center_y, radius):
        """
        Determina si el rectángulo se interseca con un círculo de radio r
        encontrando el punto más cercano de la caja al centro del círculo.
        """
        closest_x = max(self.x_min, min(center_x, self.x_max))
        closest_y = max(self.y_min, min(center_y, self.y_max))
        dist_to_closest = math.hypot(center_x - closest_x, center_y - closest_y)
        return dist_to_closest <= radius

    def intersects_box(self, other):
        """Verifica si dos rectángulos se solapan."""
        return (
            abs(self.center_x - other.center_x) <= (self.half_width + other.half_width) and
            abs(self.center_y - other.center_y) <= (self.half_height + other.half_height)
        )

    # Alias en español y alternativos
    contiene = contains
    intersc_circulo = intersects_circle

Rectangulo = BoundingBox
AABB = BoundingBox


class QuadTree:
    """
    Estructura de datos Quadtree (PR-QuadTree) optimizada para búsquedas espaciales 2D.
    Almacena los puntos exclusivamente en los nodos hoja para máxima eficiencia.
    """
    def __init__(self, boundary, capacity=16, cap=None):
        self.boundary = boundary
        self.capacity = cap if cap is not None else capacity
        self.points = []
        self.divided = False

        # Cuadrantes hijos
        self.north_west = None
        self.north_east = None
        self.south_west = None
        self.south_east = None

    def subdivide(self):
        """Divide el área en cuatro cuadrantes hijos de igual tamaño."""
        half_w = self.boundary.half_width / 2.0
        half_h = self.boundary.half_height / 2.0
        cx = self.boundary.center_x
        cy = self.boundary.center_y

        self.north_west = QuadTree(BoundingBox(cx - half_w, cy + half_h, half_w, half_h), self.capacity)
        self.north_east = QuadTree(BoundingBox(cx + half_w, cy + half_h, half_w, half_h), self.capacity)
        self.south_west = QuadTree(BoundingBox(cx - half_w, cy - half_h, half_w, half_h), self.capacity)
        self.south_east = QuadTree(BoundingBox(cx + half_w, cy - half_h, half_w, half_h), self.capacity)
        self.divided = True

    def _insert_into_children(self, point):
        """Intenta insertar el punto en alguno de los cuatro cuadrantes hijos."""
        return (
            self.north_west.insert(point) or
            self.north_east.insert(point) or
            self.south_west.insert(point) or
            self.south_east.insert(point)
        )

    def insert(self, point):
        """
        Inserta un punto en el árbol.
        Si el nodo alcanza su capacidad, se subdivide y redistribuye sus puntos
        a los hijos (garantizando que los datos solo residan en las hojas).
        """
        if isinstance(point, (tuple, list)):
            point = Point(point[0], point[1])

        # Ignorar puntos fuera del rango del nodo
        if not self.boundary.contains(point):
            return False

        # Si aún no está lleno y es hoja, se almacena aquí
        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True

        # Si supera la capacidad y no ha sido subdividido, se subdivide
        if not self.divided:
            self.subdivide()
            # Redistribuir los puntos existentes hacia los hijos
            points_to_redistribute = self.points
            self.points = []
            for p in points_to_redistribute:
                self._insert_into_children(p)

        # Delegar la inserción del nuevo punto a los hijos
        return self._insert_into_children(point)

    def query_radius(self, center, radius, found=None):
        """
        Encuentra todos los puntos que están dentro de una distancia 'radius' del punto 'center'.
        Descarta ramas enteras que no intersectan el círculo de búsqueda.
        """
        if found is None:
            found = []

        if isinstance(center, (tuple, list)):
            center = Point(center[0], center[1])

        # Poda: si este cuadrante no toca el círculo, no hay nada que buscar aquí
        if not self.boundary.intersects_circle(center.x, center.y, radius):
            return found

        # Comprobar puntos en el nodo (hoja)
        for p in self.points:
            if center.distance_to(p) <= radius:
                found.append(p)

        # Si está dividido, propagar la búsqueda a los cuadrantes hijos
        if self.divided:
            self.north_west.query_radius(center, radius, found)
            self.north_east.query_radius(center, radius, found)
            self.south_west.query_radius(center, radius, found)
            self.south_east.query_radius(center, radius, found)

        return found

    def nearest_neighbor(self, target, initial_radius=None):
        """
        Encuentra el punto más cercano a 'target' utilizando una estrategia
        de radio creciente para podar el espacio de búsqueda.
        """
        if isinstance(target, (tuple, list)):
            target = Point(target[0], target[1])

        max_dimension = max(self.boundary.half_width, self.boundary.half_height) * 2.0

        if initial_radius is None:
            # Empezamos con un radio prudente proporcional al tamaño del mapa
            current_radius = max(max_dimension / 64.0, 1.0)
        else:
            current_radius = float(initial_radius)

        candidates = []
        max_search_limit = max_dimension * 2.0

        # Expandir radio duplicándolo hasta encontrar al menos un candidato
        while not candidates and current_radius <= max_search_limit:
            candidates = self.query_radius(target, current_radius)
            if not candidates:
                current_radius *= 2.0

        if not candidates:
            # Si aún no hay candidatos, recuperar todos los puntos como respaldo
            candidates = self.get_all_points()

        if not candidates:
            return None

        # El más cercano dentro del conjunto filtrado
        return min(candidates, key=lambda p: target.distance_to(p))

    def k_nearest_neighbors(self, target, k=5, initial_radius=None):
        """
        Encuentra los k vecinos más cercanos a 'target' mediante búsqueda de radio creciente.
        """
        if isinstance(target, (tuple, list)):
            target = Point(target[0], target[1])

        max_dimension = max(self.boundary.half_width, self.boundary.half_height) * 2.0
        if initial_radius is None:
            current_radius = max(max_dimension / 64.0, 1.0)
        else:
            current_radius = float(initial_radius)

        candidates = []
        max_search_limit = max_dimension * 2.0

        while len(candidates) < k and current_radius <= max_search_limit:
            candidates = self.query_radius(target, current_radius)
            if len(candidates) < k:
                current_radius *= 2.0

        if len(candidates) < k:
            candidates = self.get_all_points()

        return sorted(candidates, key=lambda p: target.distance_to(p))[:k]

    def get_all_points(self, collected=None):
        """Recupera todos los puntos almacenados en el árbol."""
        if collected is None:
            collected = []
        collected.extend(self.points)
        if self.divided:
            self.north_west.get_all_points(collected)
            self.north_east.get_all_points(collected)
            self.south_west.get_all_points(collected)
            self.south_east.get_all_points(collected)
        return collected

    # Alias en español para mantener compatibilidad
    insertar = insert
    busca_radio = query_radius
    vecino_cercano = nearest_neighbor
    k_vecinos_cercanos = k_nearest_neighbors
    k_vecinos = k_nearest_neighbors


Quadtree = QuadTree


# =====================================================================
# Funciones de Fuerza Bruta (Para comparación en analisis.py y test.py)
# =====================================================================

def brute_force_radius(points, center, radius):
    """Búsqueda lineal O(N) de puntos dentro de un radio."""
    if isinstance(center, (tuple, list)):
        center = Point(center[0], center[1])
    return [p for p in points if center.distance_to(p) <= radius]


def brute_force_nearest_neighbor(points, target):
    """Búsqueda lineal O(N) del vecino más cercano."""
    if not points:
        return None
    if isinstance(target, (tuple, list)):
        target = Point(target[0], target[1])
    return min(points, key=lambda p: target.distance_to(p))
