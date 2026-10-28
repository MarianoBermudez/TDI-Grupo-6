import os
import math
import zipfile
import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.use('Agg')

def calculate_entropy_and_redundancy(filepath):
    """
    [a] Lee un archivo arbitrario byte por byte en tiempo O(N)
    y calcula la distribución de probabilidades, la entropía empírica de Shannon y la redundancia.
    """
    counts = [0] * 256
    total_bytes = 0
    
    # Lectura eficiente en bloques de 64 KB (Tiempo O(N), siendo N el tamaño del archivo)
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            for b in chunk:
                counts[b] += 1
                total_bytes += 1
                
    if total_bytes == 0:
        return [0.0] * 256, 0.0, 100.0, 0
        
    probs = [c / total_bytes for c in counts]
    
    # Cálculo de Entropía de Shannon: H(X) = - sum( p(x_i) * log2(p(x_i)) )
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)
            
    max_entropy = 8.0  # log2(256) bits/byte
    redundancy = 100.0 * (1.0 - (entropy / max_entropy))
    
    return probs, entropy, redundancy, total_bytes

def create_demo_files(txt_path, zip_path):
    """
    Crea un archivo de texto en español variado y representativo (~70 KB) y su versión .ZIP.
    """
    parrafos = [
        "La Teoría de la Información es una disciplina matemática desarrollada fundamentalmente por Claude E. Shannon en 1948. ",
        "Esta teoría establece los límites fundamentales en la compresión, almacenamiento y transmisión de datos a través de canales con o sin ruido. ",
        "En un archivo de texto plano, las letras no aparecen con la misma frecuencia: las vocales como la 'a' y la 'e', así como los espacios en blanco, son sumamente comunes. ",
        "Por el contrario, letras como la 'x', la 'w' o la 'z' son extremadamente infrecuentes. Además, existen reglas sintácticas y semánticas estrictas en el lenguaje natural. ",
        "Esta falta de uniformidad probabilística genera una redundancia estructural considerable, permitiendo que algoritmos de compresión como DEFLATE, LZ77 y Huffman reduzcan su tamaño. ",
        "Al aplicar un algoritmo de compresión sin pérdida como ZIP o RAR, el compresor identifica patrones repetidos y los reemplaza por referencias o códigos de longitud variable óptimos. ",
        "Como resultado directo, los bytes del archivo comprimido resultante carecen de patrones predecibles y presentan una distribución de probabilidad prácticamente uniforme. ",
        "En consecuencia, la entropía empírica del archivo comprimido se aproxima al límite máximo de 8 bits por byte, comportándose a nivel estadístico como ruido pseudoaleatorio. "
    ]
    
    contenido = ""
    for i in range(400):
        contenido += parrafos[i % len(parrafos)] + f" (Sección {i+1})\n"
        
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
        
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(txt_path, arcname=os.path.basename(txt_path))

def run_analysis(txt_path, zip_path, output_img_path):
    if not os.path.exists(txt_path) or not os.path.exists(zip_path):
        raise FileNotFoundError("Uno o ambos archivos especificados no existen.")
        
    print("=== [a & b] ANÁLISIS DE ENTROPÍA Y REDUNDANCIA (TXT vs ZIP) ===")
    txt_probs, txt_entropy, txt_redundancy, txt_size = calculate_entropy_and_redundancy(txt_path)
    zip_probs, zip_entropy, zip_redundancy, zip_size = calculate_entropy_and_redundancy(zip_path)
    
    print(f"  • Archivo .TXT ({os.path.basename(txt_path)}):")
    print(f"    - Tamaño:               {txt_size:,} bytes")
    print(f"    - Entropía empírica:    {txt_entropy:.6f} bits/símbolo (byte)")
    print(f"    - Redundancia (R):      {txt_redundancy:.2f}%")
    print()
    print(f"  • Archivo .ZIP ({os.path.basename(zip_path)}):")
    print(f"    - Tamaño:               {zip_size:,} bytes")
    print(f"    - Entropía empírica:    {zip_entropy:.6f} bits/símbolo (byte)")
    print(f"    - Redundancia (R):      {zip_redundancy:.2f}%")
    print()
    print(f"  • Relación de compresión: {txt_size / zip_size:.2f}:1 (Ahorro del {100*(1 - zip_size/txt_size):.2f}% de espacio)")
    
if __name__ == '__main__':
    demo_txt = "texto.txt"
    demo_zip = "texto.zip"
    create_demo_files(demo_txt, demo_zip)
    run_analysis(demo_txt, demo_zip, "histogramas_texto_zip.png")