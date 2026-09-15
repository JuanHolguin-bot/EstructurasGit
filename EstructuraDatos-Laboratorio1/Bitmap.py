import numpy as np

# 1. Creamos un arreglo temporal con 100,000 ceros y otro con 100,000 unos
zeros_row = np.zeros(100000, dtype=np.uint8)
ones_row = np.ones(100000, dtype=np.uint8)

# 2. Empaquetamos los bits (100,000 bits / 8 = 12,500 bytes por fila)
# np.packbits convierte cada grupo de 8 elementos en 1 solo byte
row0_packed = np.packbits(zeros_row)
row1_packed = np.packbits(ones_row)

print(f"Tamaño exacto de cada fila empaquetada: {row0_packed.nbytes} bytes")


# 3. Abrimos el archivo en modo binario de escritura ("wb")
with open("matriz_bitmap.bin", "wb") as f:
  for i in range(100000):
    # Alternamos filas de ceros y unos escribiendo los bytes directamente
    if i % 2 == 0:
      f.write(row0_packed.tobytes())
    else:
      f.write(row1_packed.tobytes())
