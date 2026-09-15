Laboratorio 1:  Optimización de Memoria para Matriz Masiva (100,000 x 100,000)

Estudiante: Juan Sebastián Holguín Suárez   

---
Descripción: 
Este repositorio resuelve el desafío de procesar, almacenar y verificar una matriz masiva de 100,000 × 100,000 elementos (10,000 millones de datos) evitando el colapso de la memoria RAM, escritura optimizada por bloques y lectura secuencial.

## Archivos del Repositorio
`matrix100k.py`: Script encargado de construir eficientemente las filas de la matriz y escribirlas de manera secuencial en un archivo de texto plano (`matriz_gigante.txt`) en el disco duro. 
  1. Composición Horizontal de las Filas
    Cada fila del archivo es una secuencia continua de texto horizontal compuesta exactamente por 100,000 elementos numéricos separados por comas (,). Se definen dos tipos de filas base:
      Fila de ceros (fila0): Una secuencia de 100,000 ceros consecutivos (0,0,0,...,0).
      Fila de unos (fila1): Una secuencia de 100,000 unos consecutivos (1,1,1,...,1).

  2. Separación Vertical por Saltos de Línea
    Para convertir estas cadenas horizontales en una matriz estructurada, se utiliza el carácter de salto de línea (\n) como delimitador. Cada 100,000 elementos, el sistema inserta un salto de línea, lo que permite apilar los registros verticalmente uno debajo del otro.

`Lector.py`: Script diseñado para leer el archivo gigante por bloques o líneas, permitiendo verificar que cada fila contenga exactamente los 100,000 registros esperados sin consumir memoria excesiva, es decir está diseñado para verificar que si hayan 100,000 registros en cada fila

¿Cómo verificar el contenido de la matriz?
Los métodos usados fueron. 
1. El archivo `Lector.py` para verificar cantidad de columnas.
2. Por consola usar comandos para contar la cantidad de separadores de filas y verificar que hayan 100,000 o 99,999 si no se tiene en cuenta el último.


Por fines de practicidad y en el contexto de Linux, en clase se usó como separador entre cada fila el carácter "|"; (0,0,...,0) | (1,1,...,1), se puede ver ilustrado en (Imagen 1), lo cual fue posible ver usando el comando `head -n 2 matriz_gigante.txt
`, que sirve para mostrar únicamente las dos primeras filas del archivo. 

Luego para verificar que si hayan 100,000 filas, se usó el comando `grep -o '|' matriz_gigante.txt | wc -l` para contar la cantidad de "|" que existían en el archivo, lo que es igual a la cantidad de filas. 
    - `grep -o '|' matriz_gigante.txt | wc -l`: Cuenta el número exacto de separadores (|) en todo el archivo; `grep -o` aísla cada coincidencia en una línea independiente y `wc -l` cuenta el total de líneas resultante, el resultado dio 100,000, lo que confirma que si hay 100,000 filas en la matriz (Imagen 2). 
  
## Solución Óptima: Matriz de Bitmaps Binarios (1.25 GB) 

Archivo - (`Bitmap.py`)

Para superar las limitaciones del texto plano (que consumía ~20 GB y saturaba el sistema), la solución definitiva implementa una matriz de bitmaps binarios utilizando Python y NumPy. Esto reduce drásticamente el espacio en disco a ~1.25 GB (exactamente 1,220,704 KB) y permite un rendimiento de lectura y escritura ultrarrápido sin comprometer la memoria RAM.

1. ¿Cómo funciona el empaquetado de bits a bytes?
En el almacenamiento tradicional de texto, un carácter (como '0' o '1') ocupa un byte completo (8 bits) a pesar de requerir un solo valor binario.
  - Para optimizar esto, la solución utiliza la función np.packbits():
  - Cada celda de la matriz almacena un único valor booleano (0 o 1).
  - En lugar de desperdiciar espacio, la función agrupa los elementos de 8 en 8 y los empaqueta dentro de los 8 bits de un único byte.
  - Ejemplo por fila: Una fila de 100,000 elementos (bits) dividida entre 8 bits por byte da como resultado un tamaño fijo de exactamente 12,500 bytes (12.2 KB) por cada fila.

2. Estructura y Composición de la Matriz
  - A diferencia de los archivos de texto, esta matriz binaria no utiliza comas (,) ni saltos de línea (\n).
  - Flujo continuo: El archivo resultante (matriz_bitmap.bin) es una secuencia binaria continua y compacta.
  - Filas alternas: El script escribe secuencialmente 50,000 filas de ceros empaquetados y 50,000 filas de unos empaquetados.
  - Acceso Directo (O(1)): Al tener todas las filas un tamaño exacto y fijo de 12,500 bytes, el sistema no necesita leer el archivo desde el inicio. Para buscar cualquier fila (por ejemplo, la fila 1,000), basta con           calcular la posición matemática exacta en el disco (1,000 * 12,500 = 12,500,000 bytes), saltar directamente a ella con el método f.seek() y descomprimir únicamente esos datos en milisegundos.

3. Verificación Estructural mediante el Tamaño del Archivo:
  Gracias a la precisión matemática del formato binario, no es necesario descomprimir los 10,000 millones de elementos para verificar que la matriz está completa y correcta. La integridad se valida directamente comprobando el peso exacto del archivo en el sistema operativo.

Justificación del tamaño (1,220,704 KB):
Cálculo en bytes: La matriz completa tiene 100,000 filas, y cada fila mide exactamente 12,500 bytes (filas) x 12,500 bytes = 1,250,000,000 bytes.
Su Conversión a Kilobytes (KB): Como en informática un Kilobyte equivale a 1,024 bytes (y no a 1,000), dividimos el total entre 1024: 1,250,000,000 bytes / 1024 = 1,220,703.125 KB Redondeando al entero superior, obtenemos exactamente 1,220,704 KB (~1.25 GB).Si el archivo en disco coincide exactamente con este valor en bytes, se comprueba de manera absoluta y matemática que la matriz de 100,000 × 100,000 se generó con éxito y sin pérdida de datos.
