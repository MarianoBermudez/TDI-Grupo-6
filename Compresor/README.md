# Práctico de Máquina 2: Desafío de Proveedores de Compresión

Repositorio institucional para el desarrollo, implementación y evaluación experimental de un algoritmo de compresión y descompresión basado en la **Transformada de Burrows-Wheeler (BWT)** y **Huffman Estático**, contrastado empíricamente frente a estándares de mercado y referencias de la cátedra.

---

## 1. Identificación y Asignación

* **Solución Propia:** Transformada de Burrows-Wheeler (BWT) combinada con codificación Huffman Estática.
* **Solución Externa (Mercado):** Zstandard configurado en Nivel 3 (`zstd -3`).
* **Baseline de Cátedra:** `gzip` configurado en Nivel 6 sin metadatos temporales (`gzip -n -6`).

---

## 2. Descripción del Algoritmo Propio

El proceso de compresión y descompresión se encuentra estructurado en etapas independientes para garantizar la modularidad y el cumplimiento estricto del paradigma sin pérdida (*lossless*):

1. **Transformada de Burrows-Wheeler (BWT):** 
   * Se procesa el bloque de bytes de entrada duplicando la secuencia para emular rotaciones cíclicas y ordenando lexicográficamente los sufijos resultantes.
   * La última columna de la matriz conceptual genera un flujo altamente redundante que agrupa bytes idénticos de manera contigua.
   * Se registra el índice numérico exacto de la rotación original (`indice_bwt`), parámetro indispensable para la reconstrucción inversa.
2. **Codificación Huffman Estática:** 
   * Cada símbolo del flujo BWT es sustituido por una representación en bits basada en un árbol de frecuencias estático universal precalculado (hardcodeado idénticamente en el compresor y descompresor).
   * Al utilizar un modelo estático predefinido, se elimina por completo la necesidad de almacenar tablas de frecuencias o diccionarios dinámicos en la cabecera del archivo comprimido.
3. **Empaquetado y Relleno (Padding):** 
   * Los bits resultantes se agrupan en octetos (bytes). Si la longitud total no es mú

---

## 3. Requisitos del Sistema y Dependencias

* **Gzip**: 
  * Comando de instalación en windows: **winget install GnuWin32.Gzip**
  * Comando de instalación en linux: Depende de la distro utilizada, pero el paquete se llama **gzip**

* **Zstandard**: 
  * Comando de instalación en windows: **winget install Facebook.Zstandard**
  * Comando de instalación en linux: Depende de la distro utilizada, pero el paquete se llama **zstd**

* **Lenguaje:** Python 3.8 o superior.

---

## 4. Instrucciones de Ejecución por Línea de Comandos (CLI)

### Compresión
Para generar un archivo comprimido propio con extensión `.tdi`: python compressor.py <archivo_entrada.txt> <archivo_salida.tdi>

### Descompresión
Para descomprimir un archivo con extensión .tdi: python descompressor.py <archivo_comprimido.tdi> <archivo_descomprimido.txt>

### Validación SHA256
Para validar con SHA256: python validador.py <archivo_entrada.txt> <archivo_descomprimido.txt>
 
### Benchmark
Para realizar el Benchmark sobre un archivo .txt: python benchmark.py <prueba.txt>

***Disclaimer***: Todos los archivos se encuentran en la carpeta tests por lo tanto en cada llamada a un archivo .py debe especificarse la ruta **ej: python compressor.py tests/prueba_2_texto_natural.txt tests/salida_prueba2.tdi**

---

## 5. Formato del Archivo Comprimido (.tdi) y Cabecera

| Campo | Tamaño (Bytes) | Tipo de Dato | Descripción Técnica | 
| --- | --- | --- | --- |
| `Magic Bytes` | `4`  | `Bytes`  | `Identificador de formato y versión: b"STA1"`  |
| `Índice BWT` | `4`  | `Entero de 32 bits (>I)`  | `Posición indexada de la fila original dentro de la matriz transformada`  |
| `Padding` | `1`  | `Entero de 8 bits (>B)`  | `Cantidad de bits de relleno aplicados para alinear el último byte del payload`  |
| `Payload` | `Variable`  | `Bytes`  | `Secuencia de bits binaria resultante de la codificación Huffman Estática`  |

---

## 6. Solución Externa y Baseline de Referencia
* **Baseline (gzip -n -6)**: Utilizado como estándar común de la cátedra para establecer la métrica base del Weissman Score ($W = 1.000$). Se ejecuta excluyendo marcas de tiempo (-n) para asegurar la reproducibilidad estricta de los archivos comprimidos.
* **Solución Externa (zstd -3)**: Algoritmo de mercado basado en FSE (Finite State Entropy) y secuencias LZ, seleccionado para contrastar el rendimiento de la implementación académica frente a tecnologías industriales de alta velocidad y compresión avanzada.

---

## 7. Ejemplo Práctico de Uso Paso a Paso

**Flujo completo de validación utilizando un archivo de prueba:**

# Paso 1: Comprimir el archivo de prueba utilizando la solución propia
python compressor.py tests/prueba_1_pequena.txt tests/prueba_1_pequena.txt.tdi

# Paso 2: Descomprimir el archivo .tdi generado para reconstruir el original
python descompressor.py tests/prueba_1_pequena.txt.tdi tests/prueba_1_recuperada.txt

# Paso 3: Validar la integridad byte a byte mediante huellas criptográficas SHA-256
python validador.py tests/prueba_1_pequena.txt tests/prueba_1_recuperada.txt

# Paso 4: Ejecutar el benchmark comparativo y registrar los resultados en la carpeta results/
python benchmark.py tests/prueba_1_pequena.txt
