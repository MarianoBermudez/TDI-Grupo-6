# PRÁCTICOS TEORÍA DE LA INFORMACIÓN - ÁREA TEMÁTICA Nº 1
Licenciatura en Ciencias de la Computación - 2026

## Grupo 6: 
- Gómez Guillermo E010-376
- Mondre Juan E010-220
- Bermúdez Mariano E010-294
- Cardó Luciano E010-203
- López Lautaro E010-233

## Organización del Repositorio
El repositorio está compuesto por la resolución de los prácticos 1 y 2 (PDF) y los ejercicios del Práctico de Máquina 1 desarrollados en python, incluyendo los archivos adicionales y de prueba según sea necesario.

## Dependencias Necesarias
El proyecto utiliza Python 3.8+ y combina librerías estándar con librerías numéricas y gráficas habituales:

- Librerías estándar de Python: os, sys, math, struct, socket, threading, random, json, zipfile.
- Librerías externas:
    - numpy: Operaciones matriciales y manejo de arreglos numéricos.
    - matplotlib: Generación y visualización de histogramas y gráficos comparativos.

Para instalar las dependencias externas necesarias, ejecute:

    pip install numpy matplotlib


## Instrucciones de Ejecución


### Scripts con Dependencia Directa de Archivos Locales

* **`analizador_audio.py`**: Requiere que los archivos `audio.wav` y `audio.mp3` existan previamente en el directorio de ejecución.
* **`analizador_imagen.py`**: Utilizando los archivos `image.bmp` e `image.jpg` del directorio actual.
* **`analizador_texto.py`**: Genera un archivo `texto.txt` (~70 KB) y su versión `texto.zip`.
* **`analizador_ic.py`**: Requiere la existencia del archivo `texto.txt` en el directorio actual (crea automáticamente `texto.zip` si no está presente).
* **`empaquetado_bitwise.py`**: Se ejecuta directamente (`python empaquetado_bitwise.py`) para generar y comparar `personas.json` y `personas.bin`.


### Scripts Interactivos por Consola (requieren entrada del usuario)

* **`capacidad_canal.py`**: Solicita ingresar manualmente por teclado las probabilidades condicionales $P(Y|X)$ para una matriz $2 \times 4$.
* **`distancia_cadenas.py`**: Solicita ingresar dos cadenas de texto por consola para calcular las distancias de Hamming, Levenshtein y su grado de similitud.
* **`deteccion_errores.py`**: Solicita ingresar un CUIT/CUIL de 11 dígitos para validar su dígito verificador mediante el algoritmo de módulo 11.


### Arquitectura Cliente-Servidor (Sockets TCP)
#### `servidor_bsc.py` y `cliente_bsc.py`

1. Abrir una primera terminal y ejecutar el servidor:
   ```bash
   python servidor_bsc.py
   ```
   *(Quedará escuchando en el puerto TCP 5555).*

2. Abrir una segunda terminal y ejecutar el cliente:
   ```bash
   python cliente_bsc.py
   ```
   *(Se conectará al servidor, ejecutará las pruebas empíricas de BER, envío de texto y cálculo de capacidad de canal).*
