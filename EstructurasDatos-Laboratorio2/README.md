# Árbol de Merkle - Implementación en Python

Este proyecto contiene una implementación de un **Árbol de Merkle** en Python (`ArbolMerkle.py`). Un árbol de Merkle, o árbol hash, es una estructura de datos en forma de árbol donde cada nodo hoja está etiquetado con el hash criptográfico de un bloque de datos (por ejemplo, una transacción), y cada nodo no hoja está etiquetado con el hash criptográfico de las etiquetas de sus nodos hijos.

Los árboles de Merkle son ampliamente utilizados en sistemas distribuidos y tecnologías blockchain (como Bitcoin y Ethereum) para verificar de manera eficiente y segura la integridad de grandes conjuntos de datos.

## Estructura del Código

El script `ArbolMerkle.py` se divide en las siguientes partes principales:

### Clases y Funciones Principales

- **`NodoMerkle`**: Una clase que define la estructura de un nodo en el árbol. Cada nodo tiene un puntero a su hijo `izquierdo`, a su hijo `derecho`, y un `valor` que almacena el hash criptográfico.
- **`obtener_hash(dato)`**: Función de utilidad que toma una cadena de texto (dato) y devuelve su hash **SHA-256** en formato hexadecimal utilizando la librería `hashlib`.
- **`construir_arbol_merkle(datos)`**: Función central que toma una lista de datos (transacciones), crea los nodos hoja iniciales (hasheando cada dato), y construye recursivamente los niveles superiores del árbol agrupando los nodos de dos en dos, concatenando sus hashes y aplicando un nuevo hash. Retorna la raíz del árbol de Merkle.

### Funciones Interactivas y de Utilidad

- **`solicitar_transacciones()`**: Solicita al usuario ingresar un número determinado de transacciones (cadenas de texto) a través de la consola para ser incluidas en el árbol.
- **`prueba_inclusion(transacciones_arbol)`**: Permite buscar si una transacción específica existe dentro del conjunto de hojas del árbol. Es una simulación simple de una prueba de inclusión.
- **`visualizar_arbol_merkle(root_node)`** y **`_draw_merkle_node(...)`**: Funciones encargadas de imprimir en la consola una representación visual del árbol de Merkle en formato de árbol de texto ASCII, lo cual facilita comprender la estructura generada. *(Nota: Estas funciones de visualización en particular se desarrollaron con la ayuda de la inteligencia artificial Gemini).*

### Menú Interactivo

- **`menu()`**: Inicia un bucle que muestra un menú interactivo en la consola con las siguientes opciones:
  1. **Construir Árbol Merkle**: Pide al usuario transacciones y genera la estructura del árbol.
  2. **Realizar Búsqueda de Transacción**: Verifica si una transacción dada se encuentra en el árbol previamente construido.
  3. **Visualizar Árbol de Merkle**: Imprime la estructura jerárquica del árbol en la terminal, mostrando los primeros caracteres de los hashes.
  4. **Salir**: Termina la ejecución del programa.


Parte del desarrollo de este código, en particular la lógica recursiva y de formato en las funciones `_draw_merkle_node` y `visualizar_arbol_merkle`, fue elaborada con el apoyo de la inteligencia artificial **Gemini**.

## EXPERIMENTOS

En la imagen `ConstrucciónArbol` se evidencia las transacciones ingresadas para construir el arbol y el valor hash de la raiz calculado (7ae6ad5cb900...)

En la imagen `VisializacionArbol` se puede ver una especie de modelo ASCII que muestra la estructura del arbol, tambien se puede evidenciar el duplicado de nodos cuando se presenta imparidad. 

Por ultimo en la imagen `Experimento` se puede evidenciar: 
  1. Se crea un nuevo arbol modificando una de las transacciones para comprobar que la raíz cambie completamente (417a3d1724bb...). 
  2. Se quiere consultar si una transacción existe en el arbol, porbando con un valor válido (123) y un valor inválido (951). 

