import hashlib
import sys

def calcular_sha256(ruta_archivo, tamano_bloque=65536):
    sha256 = hashlib.sha256()
    try:
        with open(ruta_archivo, "rb") as f:
            while bloque := f.read(tamano_bloque):
                sha256.update(bloque)
        return sha256.hexdigest()
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {ruta_archivo}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python validador.py <archivo_original> <archivo_descomprimido>")
        sys.exit(1)

    archivo_original = sys.argv[1]
    archivo_descomprimido = sys.argv[2]

    hash_orig = calcular_sha256(archivo_original)
    hash_desc = calcular_sha256(archivo_descomprimido)

    print(f"SHA-256 Original:      {hash_orig}")
    print(f"SHA-256 Descomprimido: {hash_desc}")
    print("-" * 50)

    if hash_orig == hash_desc:
        print("VALIDACIÓN EXITOSA: Los archivos son idénticos byte a byte.")
    else:
        print("ERROR: Los archivos difieren. La compresión/descompresión tuvo pérdidas.")
