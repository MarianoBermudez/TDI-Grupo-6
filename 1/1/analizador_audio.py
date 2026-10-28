import os
import sys
import math
import struct
import matplotlib.pyplot as plt
import numpy as np

# Configurar matplotlib para modo headless (no-GUI)
import matplotlib
matplotlib.use('Agg')

def parse_wav_header(filepath):
    """
    Lee y analiza dinámicamente la cabecera WAV (RIFF/WAVE),
    recorriendo los sub-bloques (chunks) hasta encontrar 'fmt ' y 'data',
    saltando bloques opcionales de metadatos como 'bext', 'LIST', 'JUNK', etc.
    """
    try:
        with open(filepath, 'rb') as f:
            # 1. Leer el encabezado principal RIFF (12 bytes: RIFF + ChunkSize + WAVE)
            riff_header = f.read(12)
            if len(riff_header) < 12:
                raise ValueError("El archivo es demasiado pequeño para ser un WAV válido.")
            
            chunk_id, chunk_size, format_tag = struct.unpack('<4sI4s', riff_header)
            if chunk_id != b'RIFF' or format_tag != b'WAVE':
                raise ValueError("El archivo no tiene la firma binaria RIFF/WAVE válida.")
            
            header_data = {
                "ChunkID": chunk_id.decode('ascii', errors='ignore'),
                "ChunkSize": chunk_size,
                "Format": format_tag.decode('ascii', errors='ignore'),
            }
            
            fmt_found = False
            
            # 2. Recorrer los sub-bloques (chunks) dinámicamente
            while True:
                # Cada bloque tiene una mini-cabecera de 8 bytes: 4 bytes (ID) + 4 bytes (Tamaño)
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break  # Fin del archivo o no hay más bloques
                
                sub_id, sub_size = struct.unpack('<4sI', chunk_header)
                sub_id_str = sub_id.decode('ascii', errors='ignore')
                
                if sub_id == b'fmt ':
                    fmt_bytes = f.read(sub_size)
                    if len(fmt_bytes) < 16:
                        raise ValueError("El bloque 'fmt ' está corrupto o es incompleto.")
                    
                    # Unpack de los metadatos de formato PCM (16 bytes estándar)
                    audio_fmt, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', fmt_bytes[:16])
                    
                    header_data["Subchunk1ID"] = sub_id_str
                    header_data["Subchunk1Size"] = sub_size
                    header_data["AudioFormat"] = audio_fmt
                    header_data["NumChannels"] = num_channels
                    header_data["SampleRate"] = sample_rate
                    header_data["ByteRate"] = byte_rate
                    header_data["BlockAlign"] = block_align
                    header_data["BitsPerSample"] = bits_per_sample
                    fmt_found = True
                    
                elif sub_id == b'data':
                    header_data["Subchunk2ID"] = sub_id_str
                    header_data["Subchunk2Size"] = sub_size
                    # Encontramos el bloque de datos de audio, finalizamos el análisis de cabecera
                    break
                else:
                    # Bloque opcional (bext, LIST, JUNK, etc.)
                    # Saltamos 'sub_size' bytes (ajustando a número par según el estándar RIFF)
                    pad = sub_size % 2
                    f.seek(sub_size + pad, 1)  # 1 = os.SEEK_CUR (posición actual)
            
            if not fmt_found:
                raise ValueError("No se encontró el sub-bloque de formato 'fmt ' en el archivo.")
                
            return header_data
            
    except Exception as e:
        raise ValueError(f"Error al analizar la cabecera WAV: {str(e)}")

def validate_files(wav_path, mp3_path):
    """
    Valida la existencia, extensiones y firmas de los archivos WAV y MP3.
    """
    print("=== [a] FASE DE CARGA Y VALIDACIÓN ===")
    
    # 1. Validación de existencia
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"No se encontró el archivo WAV en la ruta: {wav_path}")
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"No se encontró el archivo MP3 en la ruta: {mp3_path}")
        
    print(f"✔ Ambos archivos existen en el sistema.")
    
    # 2. Validación de extensiones
    if not wav_path.lower().endswith('.wav'):
        print(f"⚠ Advertencia: El archivo WAV no tiene la extensión estándar .wav: {wav_path}")
    if not mp3_path.lower().endswith('.mp3'):
        print(f"⚠ Advertencia: El archivo MP3 no tiene la extensión estándar .mp3: {mp3_path}")
        
    # 3. Validación de firmas de formato (Magic Bytes)
    # Validar WAV
    with open(wav_path, 'rb') as f:
        magic_wav = f.read(12)
        if len(magic_wav) >= 12:
            chunk_id = magic_wav[0:4]
            format_tag = magic_wav[8:12]
            if chunk_id != b'RIFF' or format_tag != b'WAVE':
                print(f"⚠ Advertencia: Las firmas binarias de {wav_path} no coinciden con un contenedor RIFF/WAVE estándar (ID: {chunk_id}, Formato: {format_tag})")
            else:
                print(f"✔ Firma binaria WAV validada con éxito ('RIFF' y 'WAVE' detectados).")
        else:
            raise ValueError("El archivo WAV está corrupto o es demasiado corto.")
            
    # Validar MP3
    with open(mp3_path, 'rb') as f:
        magic_mp3 = f.read(3)
        # ID3v2 empieza con "ID3" o frames de audio empiezan con 0xFF (bit sync)
        if len(magic_mp3) >= 3:
            if magic_mp3 == b'ID3':
                print(f"✔ Firma binaria MP3 validada con éxito (ID3v2 tag detectada).")
            elif magic_mp3[0] == 0xFF and (magic_mp3[1] & 0xE0) == 0xE0:
                print(f"✔ Firma binaria MP3 validada con éxito (Audio Frame Sync de MP3 detectado).")
            else:
                print(f"⚠ Advertencia: No se detectó la cabecera estándar ID3 o frame de sincronización en {mp3_path}. Podría ser un archivo MP3 raw sin tags.")
        else:
            raise ValueError("El archivo MP3 está corrupto o es demasiado corto.")

def calculate_distribution(filepath):
    """
    Lee un archivo byte por byte y calcula la frecuencia relativa de cada byte (0-255).
    """
    counts = [0] * 256
    total_bytes = 0
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536) # Leer en bloques de 64KB por eficiencia
            if not chunk:
                break
            for byte in chunk:
                counts[byte] += 1
                total_bytes += 1
                
    if total_bytes == 0:
        return [0.0] * 256, 0
        
    probs = [count / total_bytes for count in counts]
    return probs, total_bytes

def calculate_entropy(probs):
    """
    Calcula la entropía de Shannon a partir de una distribución de probabilidad.
    """
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def generate_histograms(wav_probs, mp3_probs, output_path):
    """
    Genera y guarda un gráfico comparativo de histogramas de frecuencias de bytes.
    """
    plt.figure(figsize=(14, 6))
    
    bytes_axis = np.arange(256)
    
    # Subplot 1: WAV
    plt.subplot(1, 2, 1)
    plt.bar(bytes_axis, wav_probs, color='royalblue', width=1.0, edgecolor='none', alpha=0.8)
    plt.title("Histograma de Frecuencias de Bytes (WAV sin compresión)", fontsize=11, fontweight='bold')
    plt.xlabel("Valor del Byte (0 - 255)", fontsize=9)
    plt.ylabel("Probabilidad (Frecuencia Relativa)", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlim(-5, 260)
    
    # Subplot 2: MP3
    plt.subplot(1, 2, 2)
    plt.bar(bytes_axis, mp3_probs, color='crimson', width=1.0, edgecolor='none', alpha=0.8)
    plt.title("Histograma de Frecuencias de Bytes (MP3 comprimido)", fontsize=11, fontweight='bold')
    plt.xlabel("Valor del Byte (0 - 255)", fontsize=9)
    plt.ylabel("Probabilidad (Frecuencia Relativa)", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlim(-5, 260)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✔ Gráficos de histogramas guardados exitosamente en: {output_path}")

def run_analysis(wav_path, mp3_path, output_img_path):
    # a) Validación
    validate_files(wav_path, mp3_path)
    print()
    
    # b) Análisis de cabecera WAV
    print("=== [b] ANÁLISIS DE LA CABECERA DEL ARCHIVO WAV (RIFF/WAVE) ===")
    wav_header = parse_wav_header(wav_path)
    for key, val in wav_header.items():
        # Formatear la salida para que sea legible
        if isinstance(val, int) and "Size" in key or "Rate" in key:
            print(f"  • {key:<15}: {val:,} {'bytes' if 'Size' in key else 'Hz' if 'Rate' in key else ''}")
        else:
            print(f"  • {key:<15}: {val}")
    print()
    
    # c) Distribución de probabilidades
    print("=== [c] CÁLCULO DE DISTRIBUCIÓN DE PROBABILIDADES ===")
    wav_probs, wav_size = calculate_distribution(wav_path)
    mp3_probs, mp3_size = calculate_distribution(mp3_path)
    print(f"  • Archivo WAV procesado: {wav_size:,} bytes analizados.")
    print(f"  • Archivo MP3 procesado: {mp3_size:,} bytes analizados.")
    print("✔ Distribuciones de probabilidad calculadas.")
    print()
    
    # d) Generación de histogramas
    print("=== [d] GENERACIÓN DE HISTOGRAMAS COMPARATIVOS ===")
    generate_histograms(wav_probs, mp3_probs, output_img_path)
    print()
    
    # e) Cálculo de entropía
    print("=== [e] CÁLCULO DE ENTROPÍA DE SHANNON ===")
    wav_entropy = calculate_entropy(wav_probs)
    mp3_entropy = calculate_entropy(mp3_probs)
    
    max_entropy = 8.0  # Para una fuente de 256 símbolos (8 bits), la entropía máxima es log2(256) = 8
    
    print(f"  • Entropía empírica de Shannon:")
    print(f"    - Archivo WAV (sin compresión): {wav_entropy:.6f} bits/símbolo (byte)")
    print(f"    - Archivo MP3 (comprimido):     {mp3_entropy:.6f} bits/símbolo (byte)")
    print(f"  • Redundancia de la fuente (R = 1 - H/H_max):")
    print(f"    - Archivo WAV: {100 * (1 - wav_entropy/max_entropy):.2f}%")
    print(f"    - Archivo MP3: {100 * (1 - mp3_entropy/max_entropy):.2f}%")
    print()
    return wav_header, wav_entropy, mp3_entropy, wav_size, mp3_size

if __name__ == '__main__':
    wav_file = "audio.wav"
    mp3_file = "audio.mp3"
    output_img = "histogramas_audio.png"
        
    run_analysis(wav_file, mp3_file, output_img)
