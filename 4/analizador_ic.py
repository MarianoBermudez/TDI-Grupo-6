import os
import math
import zipfile
import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')

def calculate_metrics(filepath):
    """
    Calcula la Entropía de Shannon, Redundancia e Índice de Coincidencia (IC)
    tanto a nivel de Bytes (0-255) como a nivel de Letras (A-Z de 27 caracteres).
    """
    with open(filepath, 'rb') as f:
        data = f.read()
        
    N_bytes = len(data)
    if N_bytes < 2:
        return None
        
    # --- 1. CÁLCULO A NIVEL DE BYTES (0-255) ---
    byte_counts = [0] * 256
    for b in data:
        byte_counts[b] += 1
        
    # Entropía de Shannon
    entropy_bytes = 0.0
    for c in byte_counts:
        if c > 0:
            p = c / N_bytes
            entropy_bytes -= p * math.log2(p)
            
    max_entropy = 8.0  # log2(256)
    redundancy_bytes = 100.0 * (1.0 - (entropy_bytes / max_entropy))
    
    # Índice de Coincidencia (IC) en Bytes: sum(f_i * (f_i - 1)) / (N * (N - 1))
    ic_bytes_num = sum(c * (c - 1) for c in byte_counts)
    ic_bytes = ic_bytes_num / (N_bytes * (N_bytes - 1))
    
    # --- 2. CÁLCULO A NIVEL DE LETRAS (Alfabeto Español / A-Z) ---
    # Convertimos texto a minúsculas y filtramos caracteres alfabéticos
    # Incluimos a-z y 'ñ'
    letter_counts = {}
    N_letters = 0
    
    # Intentar decodificar como utf-8 / latin-1
    text = ""
    try:
        text = data.decode('utf-8', errors='ignore').lower()
    except:
        text = data.decode('latin-1', errors='ignore').lower()
        
    for char in text:
        if 'a' <= char <= 'z' or char == 'ñ':
            letter_counts[char] = letter_counts.get(char, 0) + 1
            N_letters += 1
            
    if N_letters > 1:
        ic_letters_num = sum(c * (c - 1) for c in letter_counts.values())
        ic_letters = ic_letters_num / (N_letters * (N_letters - 1))
    else:
        ic_letters = 0.0
        
    return {
        "N_bytes": N_bytes,
        "Entropy_bytes": entropy_bytes,
        "Redundancy_bytes": redundancy_bytes,
        "IC_bytes": ic_bytes,
        "N_letters": N_letters,
        "IC_letters": ic_letters,
        "byte_counts": byte_counts
    }

def generate_comparison_plot(txt_metrics, zip_metrics, output_path):
    """
    Genera un gráfico comparativo de Entropía vs Índice de Coincidencia.
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    # Subplot 1: Entropía vs IC
    categories = ['Texto (.TXT)', 'Comprimido (.ZIP)']
    entropies = [txt_metrics['Entropy_bytes'], zip_metrics['Entropy_bytes']]
    ic_values = [txt_metrics['IC_letters'], 1/256] # IC esperado o medido
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax1 = axes[0]
    rects1 = ax1.bar(x - width/2, entropies, width, label='Entropía (bits/byte)', color='royalblue')
    ax1.set_ylabel('Entropía (bits/byte)', color='royalblue', fontweight='bold')
    ax1.set_ylim(0, 9)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax2 = ax1.twinx()
    ic_plot_vals = [txt_metrics['IC_letters'], zip_metrics['IC_bytes']]
    rects2 = ax2.bar(x + width/2, ic_plot_vals, width, label='Índice de Coincidencia (IC)', color='crimson')
    ax2.set_ylabel('Índice de Coincidencia (IC)', color='crimson', fontweight='bold')
    ax2.set_ylim(0, 0.10)
    
    # Líneas de referencia para IC
    ax2.axhline(0.074, color='darkgreen', linestyle=':', label='IC Español Teórico (0.074)')
    ax2.axhline(0.038, color='orange', linestyle=':', label='IC Aleatorio 27 let. (0.038)')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontweight='bold')
    ax1.set_title("Comparativa: Entropía vs. Índice de Coincidencia", fontsize=11, fontweight='bold')
    
    # Añadir valores sobre las barras
    for rect in rects1:
        height = rect.get_height()
        ax1.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
                    
    for rect in rects2:
        height = rect.get_height()
        ax2.annotate(f'{height:.4f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
                    
    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)
    
    # Subplot 2: Distribución de frecuencias de bytes
    ax_dist = axes[1]
    ax_dist.plot(txt_metrics['byte_counts'], label='Texto (.TXT)', color='royalblue', alpha=0.8)
    ax_dist.plot(zip_metrics['byte_counts'], label='Comprimido (.ZIP)', color='crimson', alpha=0.8)
    ax_dist.set_title("Distribución de Frecuencia de Bytes", fontsize=11, fontweight='bold')
    ax_dist.set_xlabel("Valor del Byte (0-255)")
    ax_dist.set_ylabel("Frecuencia Absoluta")
    ax_dist.grid(True, linestyle='--', alpha=0.5)
    ax_dist.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def main():
    txt_path = "texto.txt"
    zip_path = "texto.zip"
    
    # Crear el zip de prueba si no existe
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(txt_path, arcname="teoria_de_la_informacion.txt")
        
    txt_m = calculate_metrics(txt_path)
    zip_m = calculate_metrics(zip_path)
    
    print("=== CÁLCULO DE ENTROPÍA E ÍNDICE DE COINCIDENCIA (IC) ===")
    print(f"1. ARCHIVO DE TEXTO (.TXT): {txt_path}")
    print(f"   • Tamaño:                       {txt_m['N_bytes']:,} bytes")
    print(f"   • Entropía de Shannon (H):       {txt_m['Entropy_bytes']:.6f} bits/byte")
    print(f"   • Redundancia (R):              {txt_m['Redundancy_bytes']:.2f}%")
    print(f"   • IC a nivel de Letras (A-Z):   {txt_m['IC_letters']:.6f}  (Teórico español: ~0.074)")
    print(f"   • IC a nivel de Bytes (0-255):  {txt_m['IC_bytes']:.6f}")
    print()
    print(f"2. ARCHIVO COMPRIMIDO (.ZIP): {zip_path}")
    print(f"   • Tamaño:                       {zip_m['N_bytes']:,} bytes")
    print(f"   • Entropía de Shannon (H):       {zip_m['Entropy_bytes']:.6f} bits/byte")
    print(f"   • Redundancia (R):              {zip_m['Redundancy_bytes']:.2f}%")
    print(f"   • IC a nivel de Bytes (0-255):  {zip_m['IC_bytes']:.6f}  (Teórico aleatorio 256: ~0.0039)")
    print()
    
    out_img = "comparativa_entropia_ic.png"
    generate_comparison_plot(txt_m, zip_m, out_img)
    print(f"✔ Gráfico comparativo guardado en: {out_img}")

if __name__ == '__main__':
    main()
