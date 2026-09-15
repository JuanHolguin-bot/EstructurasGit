file_path = "matriz_gigante.txt"
sep_fila = "\n"

# Se incializa una variable para almacenar la primera fila leída del archivo
primera_fila_texto = ""

# Lectura eficiente: lee bloques pequeños hasta dar con el primer separador '\n'
with open(file_path, "r", encoding="utf-8") as f:
    while True:
        chunk = f.read(1024 * 1024)  # Lee bloques de 1 MB en lugar de cargar todo el archivo en memoria
        if not chunk:
            break

        if sep_fila in chunk:
            # Toma solo lo que está antes del primer '\n', es decir, si el fragmento de 1MB está vacío significa que ya no hay más datos que leer, por lo que se rompe el bucle
            primera_fila_texto += chunk.split(sep_fila)[0] #Verifica si el separador de fila está en el fragmento leído, si es así, toma solo la parte antes del primer salto de línea y rompe el bucle
            break
        else:
            primera_fila_texto += chunk

# Separa los números quitando las comas (obtenemos una lista de caracteres '0'), para posteriormente contar cuántos ceros hay en la primera fila
elementos = primera_fila_texto.split(",")

cantidad_ceros = elementos.count("0")
total_datos = len(elementos)

print(f"Total de datos (números) en la primera fila: {total_datos}")
print(f"Cantidad de ceros: {cantidad_ceros}")

if total_datos == 100000 and cantidad_ceros == 100000:
    print(
        " ¡Verificación exitosa! La primera fila tiene exactamente 100,000 ceros."
    )
else:
    print(" Advertencia: La fila no contiene los 100,000 datos esperados.")