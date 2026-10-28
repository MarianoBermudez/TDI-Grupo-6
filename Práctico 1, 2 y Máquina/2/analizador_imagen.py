import os
import math
import struct
import matplotlib.pyplot as plt
import numpy as np

# Configurar matplotlib para modo sin pantalla (headless)
import matplotlib
matplotlib.use('Agg')

def parse_bmp_header(filepath):
    """
    [b] Lee y desempaqueta la cabecera estándar de un archivo BMP (54 bytes):
        - 14 bytes: BITMAPFILEHEADER
        - 40 bytes: BITMAPINFOHEADER
    """
    try:
        with open(filepath, 'rb') as f:
            header_bytes = f.read(54)
            if len(header_bytes) < 54:
                raise ValueError("El archivo es demasiado pequeño para contener una cabecera BMP de 54 bytes.")
            
            # 1. BITMAPFILEHEADER (14 bytes)
            # <2sI4sI -> 2s: Signature ("BM"), I: FileSize, 4s: Reserved (4 bytes), I: DataOffset
            file_header = struct.unpack('<2sI4sI', header_bytes[0:14])
            signature = file_header[0].decode('ascii', errors='ignore')
            file_size = file_header[1]
            data_offset = file_header[3]
            
            if signature != 'BM':
                raise ValueError(f"Firma BMP inválida: se esperaba 'BM', se obtuvo '{signature}'.")
                
            # 2. BITMAPINFOHEADER (40 bytes)
            # <IiiHHIIiiII
            info_header = struct.unpack('<IiiHHIIiiII', header_bytes[14:54])
            
            header_data = {
                "Signature": signature,
                "FileSize": file_size,
                "DataOffset": data_offset,
                "HeaderSize": info_header[0],
                "Width": info_header[1],
                "Height": abs(info_header[2]),  # Puede ser negativo si es top-down
                "Planes": info_header[3],
                "BitCount": info_header[4],    # Profundidad de color (e.g. 24 bits)
                "Compression": info_header[5], # 0 = BI_RGB (Sin compresión)
                "ImageSize": info_header[6],
                "XPixelsPerM": info_header[7],
                "YPixelsPerM": info_header[8],
                "ColorsUsed": info_header[9],
                "ColorsImportant": info_header[10]
            }
            return header_data
    except Exception as e:
        raise ValueError(f"Error al analizar la cabecera BMP: {str(e)}")

def validate_image_files(bmp_path, jpg_path):
    """
    [a] Solicita y valida la existencia, extensiones y firmas binarias (magic bytes).
    """
    print("=== [a] FASE DE CARGA Y VALIDACIÓN ===")
    if not os.path.exists(bmp_path) or not os.path.exists(jpg_path):
        raise FileNotFoundError("Uno o ambos archivos de imagen no existen en la ruta provista.")
        
    print("✔ Ambos archivos existen en el sistema.")
    
    # Validar firma binaria de BMP ('BM' = 0x42 0x4D)
    with open(bmp_path, 'rb') as f:
        magic_bmp = f.read(2)
        if magic_bmp != b'BM':
            print("⚠ Advertencia: El archivo BMP no posee la firma binaria 'BM' estándar.")
        else:
            print("✔ Firma binaria BMP validada con éxito ('BM' detectado).")
            
    # Validar firma binaria de JPG/JPEG (0xFF 0xD8 0xFF)
    with open(jpg_path, 'rb') as f:
        magic_jpg = f.read(3)
        if magic_jpg != b'\xff\xd8\xff':
            print("⚠ Advertencia: El archivo JPG no posee los bytes de inicio SOI (0xFFD8FF) estándar.")
        else:
            print("✔ Firma binaria JPG validada con éxito (SOI 0xFFD8FF detectado).")

def calculate_distribution(filepath):
    """
    [c] Lee el archivo byte por byte (0 al 255) y calcula la distribución de probabilidad p(x_i).
    """
    counts = [0] * 256
    total_bytes = 0
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)  # Lectura eficiente en bloques
            if not chunk:
                break
            for b in chunk:
                counts[b] += 1
                total_bytes += 1
                
    if total_bytes == 0:
        return [0.0] * 256, 0
    probs = [c / total_bytes for c in counts]
    return probs, total_bytes

def calculate_entropy(probs):
    """
    [e] Calcula la entropía empírica utilizando la fórmula de Shannon:
        H(X) = - sum( p(x_i) * log2(p(x_i)) )
    """
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def generate_histograms(bmp_probs, jpg_probs, output_path):
    """
    [d] Genera y exporta el gráfico de histograma de frecuencias para ambos archivos.
    """
    plt.figure(figsize=(14, 6))
    bytes_axis = np.arange(256)
    
    # Calcular el valor máximo global y añadir un 5% de margen superior
    max_y = max(np.max(bmp_probs), np.max(jpg_probs)) * 1.05
    
    # Histograma BMP
    plt.subplot(1, 2, 1)
    plt.bar(bytes_axis, bmp_probs, color='seagreen', width=1.0, edgecolor='none', alpha=0.8)
    plt.title("Histograma de Frecuencias (BMP - Sin Compresión Espacial)", fontsize=11, fontweight='bold')
    plt.xlabel("Valor del Byte (0 - 255)")
    plt.ylabel("Probabilidad (Frecuencia Relativa)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlim(-5, 260)
    plt.ylim(0, max_y) # Aplicar escala unificada
    
    # Histograma JPG
    plt.subplot(1, 2, 2)
    plt.bar(bytes_axis, jpg_probs, color='darkorange', width=1.0, edgecolor='none', alpha=0.8)
    plt.title("Histograma de Frecuencias (JPG)", fontsize=11, fontweight='bold')
    plt.xlabel("Valor del Byte (0 - 255)")
    plt.ylabel("Probabilidad (Frecuencia Relativa)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlim(-5, 260)
    plt.ylim(0, max_y) # Aplicar escala unificada
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✔ Gráficos de histogramas guardados exitosamente en: {output_path}")

    
def run_analysis(bmp_path, jpg_path, output_img_path):
    validate_image_files(bmp_path, jpg_path)
    print()
    
    print("=== [b] ANÁLISIS DE LA CABECERA DEL ARCHIVO BMP (54 BYTES) ===")
    bmp_header = parse_bmp_header(bmp_path)
    
    comp_names = {0: "BI_RGB (Sin compresión)", 1: "BI_RLE8", 2: "BI_RLE4", 3: "BI_BITFIELDS"}
    
    for key, val in bmp_header.items():
        if key == "Compression":
            desc = comp_names.get(val, f"Otro ({val})")
            print(f"  • {key:<15}: {val} [{desc}]")
        elif isinstance(val, int) and ("Size" in key or "Offset" in key):
            print(f"  • {key:<15}: {val:,} bytes")
        elif isinstance(val, int) and ("Width" in key or "Height" in key or "Pixels" in key):
            print(f"  • {key:<15}: {val:,} px" if "Pixels" not in key else f"  • {key:<15}: {val:,} px/m")
        else:
            print(f"  • {key:<15}: {val}")
    print()
    
    print("=== [c] CÁLCULO DE DISTRIBUCIÓN DE PROBABILIDADES ===")
    bmp_probs, bmp_size = calculate_distribution(bmp_path)
    jpg_probs, jpg_size = calculate_distribution(jpg_path)
    print(f"  • Archivo BMP procesado: {bmp_size:,} bytes analizados.")
    print(f"  • Archivo JPG procesado: {jpg_size:,} bytes analizados.")
    print(f"  • Relación de compresión: {bmp_size / jpg_size:.2f}:1 (Reducción del {100*(1 - jpg_size/bmp_size):.2f}% de espacio)")
    print("✔ Distribuciones de probabilidad calculadas.")
    print()
    
    print("=== [d] GENERACIÓN DE HISTOGRAMAS COMPARATIVOS ===")
    generate_histograms(bmp_probs, jpg_probs, output_img_path)
    print()
    
    print("=== [e] CÁLCULO DE ENTROPÍA DE SHANNON ===")
    bmp_entropy = calculate_entropy(bmp_probs)
    jpg_entropy = calculate_entropy(jpg_probs)
    max_entropy = 8.0  # log2(256)
    
    print(f"  • Entropía empírica de Shannon:")
    print(f"    - Archivo BMP (sin compresión): {bmp_entropy:.6f} bits/símbolo (byte)")
    print(f"    - Archivo JPG (comprimido):     {jpg_entropy:.6f} bits/símbolo (byte)")
    print(f"  • Redundancia de la fuente (R = 1 - H/H_max):")
    print(f"    - Archivo BMP: {100 * (1 - bmp_entropy/max_entropy):.2f}%")
    print(f"    - Archivo JPG: {100 * (1 - jpg_entropy/max_entropy):.2f}%")
    print()

if __name__ == '__main__':
    run_analysis("image.bmp", "image.jpg", "histogramas_imagen.png")