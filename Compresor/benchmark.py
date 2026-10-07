import os
import subprocess
import time
import math
import sys

def run_cmd(cmd):
    start = time.perf_counter()
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (time.perf_counter() - start) * 1000

def run_benchmark(input_file):
    if not os.path.exists(input_file):
        print(f"Archivo {input_file} no encontrado.")
        return

    s_orig = os.path.getsize(input_file)
    print(f"Benchmarking: {input_file} ({s_orig} bytes)\n")

    # 1. Baseline: gzip -n -6
    gzip_out = input_file + ".gz"
    t_gzip = run_cmd(f"gzip -n -6 -k -f {input_file}")
    s_gzip = os.path.getsize(gzip_out)
    r_gzip = s_orig / s_gzip

    # 2. Solución de mercado: zstd -3
    zstd_out = input_file + ".zst"
    t_zstd = run_cmd(f"zstd -3 -f -q {input_file}")
    s_zstd = os.path.getsize(zstd_out)
    r_zstd = s_orig / s_zstd

    # 3. Solución Propia: BWT + Huffman
    tdi_out = input_file + ".tdi"
    start_propio = time.perf_counter()
    subprocess.run([sys.executable, "compressor.py", input_file, tdi_out], check=True, stdout=subprocess.DEVNULL)
    t_propio = (time.perf_counter() - start_propio) * 1000
    s_propio = os.path.getsize(tdi_out)
    r_propio = s_orig / s_propio

    # Weissman Score (Alpha = 1)
    # W = 1 * (R / R_ref) * (log(T_ref) / log(T))
    # Prevenir divisiones por cero o logaritmos de tiempos muy bajos
    safe_t_gzip = max(t_gzip, 1.1)
    
    w_zstd = 1 * (r_zstd / r_gzip) * (math.log(safe_t_gzip) / math.log(max(t_zstd, 1.1)))
    w_propio = (r_propio / r_gzip) * (math.log(safe_t_gzip) / math.log(max(t_propio, 1.1)))
    
    # Resultados en consola
    print(f"{'Algoritmo':<15} | {'Tamaño (B)':<12} | {'Ratio':<8} | {'Ahorro %':<10} | {'Tiempo (ms)':<12} | {'Weissman':<8}")
    print("-" * 75)
    print(f"{'gzip-6 (Base)':<15} | {s_gzip:<12} | {r_gzip:<8.3f} | {(1-s_gzip/s_orig)*100:<10.2f} | {t_gzip:<12.2f} | 1.000")
    print(f"{'Zstd-3 (Mdo)':<15} | {s_zstd:<12} | {r_zstd:<8.3f} | {(1-s_zstd/s_orig)*100:<10.2f} | {t_zstd:<12.2f} | {w_zstd:.3f}")
    print(f"{'BWT+Huffman':<15} | {s_propio:<12} | {r_propio:<8.3f} | {(1-s_propio/s_orig)*100:<10.2f} | {t_propio:<12.2f} | {w_propio:.3f}")

    # Guardar automáticamente en la carpeta results/
    os.makedirs("results", exist_ok=True)
    csv_path = f'results/resultados_benchmark_{os.path.basename(input_file).removesuffix(".txt")}.csv'
    
    # Si el archivo no existe, escribimos la cabecera
    escribir_cabecera = not os.path.exists(csv_path)
    with open(csv_path, "a", encoding="utf-8") as f_csv:
        if escribir_cabecera:
            f_csv.write("Archivo,Algoritmo,Tamano_Original,Tamano_Comprimido,Ratio,Ahorro_Pct,Tiempo_ms,Weissman\n")
        f_csv.write(f"{input_file},gzip-6,{s_orig},{s_gzip},{r_gzip:.3f},{(1-s_gzip/s_orig)*100:.2f},{t_gzip:.2f},1.000\n")
        f_csv.write(f"{input_file},Zstd-3,{s_orig},{s_zstd},{r_zstd:.3f},{(1-s_zstd/s_orig)*100:.2f},{t_zstd:.2f},{w_zstd:.3f}\n")
        f_csv.write(f"{input_file},BWT+Huffman,{s_orig},{s_propio},{r_propio:.3f},{(1-s_propio/s_orig)*100:.2f},{t_propio:.2f},{w_propio:.3f}\n")

    # Limpieza
    for ext in [gzip_out, zstd_out, tdi_out]:
        if os.path.exists(ext): os.remove(ext)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python benchmark.py <archivo_prueba.txt>")
    else:
        run_benchmark(sys.argv[1])
