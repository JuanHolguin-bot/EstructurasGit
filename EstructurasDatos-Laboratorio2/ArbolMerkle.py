import hashlib

class NodoMerkle:
    def __init__(self, izquierdo, derecho, valor):
        self.izquierdo = izquierdo
        self.derecho = derecho
        self.valor = valor

def obtener_hash(dato):
    return hashlib.sha256(dato.encode('utf-8')).hexdigest()

def construir_arbol_merkle(datos):
    if not datos:
        return None

    # Crear nodos hoja iniciales
    nodos = [NodoMerkle(None, None, obtener_hash(d)) for d in datos]

    # Construir el árbol hacia arriba hasta llegar a la raíz
    while len(nodos) > 1:
        nivel_siguiente = []

        # Si el número de nodos es impar, duplicar el último
        if len(nodos) % 2 != 0:
            nodos.append(nodos[-1])

        for i in range(0, len(nodos), 2):
            izq = nodos[i]
            der = nodos[i+1]
            # Combinar los valores de los hijos
            combinado = izq.valor + der.valor
            padre_valor = obtener_hash(combinado)
            nodo_padre = NodoMerkle(izq, der, padre_valor)
            nivel_siguiente.append(nodo_padre)

        nodos = nivel_siguiente

    return nodos[0] # Retorna la raíz de Merkle


def solicitar_transacciones():
  """Solicita al usuario un número de transacciones y las ingresa."""
  numero_transacciones = int(input("Ingrese el número de transacciones para construir el árbol Merkle: "))
  transacciones = []
  for i in range(numero_transacciones):
    transaccion = input(f"Ingrese la transacción {i+1}: ")
    transacciones.append(transaccion)
  return transacciones

def prueba_inclusion(transacciones_arbol):
  if not transacciones_arbol:
      print("No hay un árbol construido para realizar la búsqueda.")
      return

  print("\n--- Búsqueda de Transacción en Hojas ---")
  transacciones_revisar = input("Ingrese la transacción que desea buscar en las hojas: ")
  hashed_transaccion_revisar = obtener_hash(transacciones_revisar) # obtener_hash is defined in cell 49fa04ab

  encontrado = False
  for block in transacciones_arbol:
      if obtener_hash(block) == hashed_transaccion_revisar:
          encontrado = True
          break

  if encontrado:
      print(f"\n ¡La transacción '{transacciones_revisar}' fue ENCONTRADA ✅ en las hojas del árbol!")
  else:
      print(f"\n La transacción '{transacciones_revisar}' NO fue encontrada ❌ en las hojas del árbol.")

def _draw_merkle_node(node, prefix, is_last):
    """
    Función auxiliar recursiva para dibujar los nodos del árbol Merkle en formato ASCII.
    """
    if node is None:
        return

    # Determinar el conector y el tipo de nodo (Hoja o Nodo interno)
    connector = "└── " if is_last else "├── "
    node_type = "Hoja" if node.izquierdo is None and node.derecho is None else "Nodo"

    # Imprimir el nodo actual
    print(f"{prefix}{connector}{node_type}: {node.valor[:8]}...")

    # Preparar el prefijo para los hijos
    if node.izquierdo or node.derecho:
        next_prefix = prefix + ("    " if is_last else "│   ")

        # El hijo izquierdo no es el último si existe un hijo derecho
        _draw_merkle_node(node.izquierdo, next_prefix, node.derecho is None)
        # El hijo derecho es siempre el último (si existe)
        _draw_merkle_node(node.derecho, next_prefix, True)

def visualizar_arbol_merkle(root_node):
  """
  Inicia la visualización del árbol Merkle en formato ASCII.
  """
  if root_node is None:
    print("Árbol Merkle vacío.")
    return

  print(f"Raíz: {root_node.valor[:8]}...")
  # Dibujar los hijos del nodo raíz
  _draw_merkle_node(root_node.izquierdo, "  ", root_node.derecho is None)
  _draw_merkle_node(root_node.derecho, "  ", True)

def menu():
  transacciones_arbol_principal = []
  raiz_arbol = None

  while True:
    print("\n-- Menú ---")
    print("1. Construir Árbol Merkle")
    print("2. Realizar Búsqueda de Transacción")
    print("3. Visualizar Árbol de Merkle")
    print("4. Salir")

    opcion = input("Seleccione una opción: ")

    if opcion == '1':
      print("--- Construcción del Árbol Merkle ---")
      transacciones_arbol_principal = solicitar_transacciones()
      if transacciones_arbol_principal:
          raiz_arbol = construir_arbol_merkle(transacciones_arbol_principal)
          print("Raíz de Merkle construida:", raiz_arbol.valor)
      else:
          print("No se ingresaron transacciones para construir el árbol Merkle.")
          raiz_arbol = None
    elif opcion == '2':
      if raiz_arbol:
          prueba_inclusion(transacciones_arbol_principal)
      else:
          print("Primero debe construir un árbol Merkle (Opción 1).")
    elif opcion == '3':
      if raiz_arbol:
          print("\n--- Visualización del Árbol Merkle ---")
          visualizar_arbol_merkle(raiz_arbol)
      else:
          print("Primero debe construir un árbol Merkle (Opción 1).")
    elif opcion == '4':
      print("Saliendo del programa.")
      break
    else:
      print("Opción inválida. Por favor, intente de nuevo.")

# Iniciar el menú
menu()