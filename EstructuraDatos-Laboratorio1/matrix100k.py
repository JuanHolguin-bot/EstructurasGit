#Se declaran dos variables de texto vacías para almacenar las filas de la matriz
fila0, fila1 = "", ""

# Construcción de las filas con comas entre elementos
for _ in range(100000):
    fila0 += "0,"
    fila1 += "1,"

# Quitamos la última coma de cada fila para no dejar una coma final
fila0 = fila0.rstrip(",")
fila1 = fila1.rstrip(",")

# Separador de filas, un salto de linea que indica el final de una fila y el inicio de otra
sep_fila = "\n"

# Escritura en el archivo
# Abre el archivo en modo escritura o lo crea en caso de no existir, en formato universal (utf-8)
with open("matriz_gigante.txt", "w", encoding="utf-8") as f:  
    for _ in range(100000 // 2): #Dado que estamos escribiendo dos filas a la vez, hacemos la mitad de iteraciones
        f.write(fila0 + sep_fila + fila1 + sep_fila)