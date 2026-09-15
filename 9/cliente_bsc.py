import socket
import struct
import random
import math

HOST = "127.0.0.1"
PUERTO = 5555

def recibir_exactamente(sock, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Conexión cerrada.")
        buf.extend(chunk)
    return bytes(buf)

def enviar_mensaje(sock, msg):
    raw = msg.encode("ascii")
    header = struct.pack("!I", len(raw))
    sock.sendall(header + raw)

def recibir_mensaje(sock):
    header = recibir_exactamente(sock, 4)
    length = struct.unpack("!I", header)[0]
    return recibir_exactamente(sock, length).decode("ascii")

def texto_a_bits(texto):
    return "".join(format(ord(c), "08b") for c in texto)

def bits_a_texto(bits):
    bytes_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return "".join(chr(int(b, 2)) for b in bytes_list if len(b) == 8)

def H(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def probar_trama(sock, n_bits):
    trama = "".join(random.choice("01") for _ in range(n_bits))
    enviar_mensaje(sock, trama)
    recibido = recibir_mensaje(sock)
    errores = sum(1 for a, b in zip(trama, recibido) if a != b)
    return trama, recibido, errores, errores / n_bits

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PUERTO))

    print("--- Fase 1: BER Empirico ---")
    tamanios = [100, 10000, 1000000]
    ber_final, trama_larga = 0.0, ""
    
    for n in tamanios:
        trama, recibido, errores, ber = probar_trama(sock, n)
        print(f"N: {n:<8} Errores: {errores:<6} BER: {ber:.6f}")
        if n == 1000000:
            ber_final = ber
            trama_larga = trama

    print("\n--- Transmision de Texto ---")
    frase = "Teoria de la Informacion 2026"
    bits_orig = texto_a_bits(frase)
    enviar_mensaje(sock, bits_orig)
    bits_rx = recibir_mensaje(sock)
    print(f"Original: {frase}")
    print(f"Recibido: {bits_a_texto(bits_rx)}")

    print("\n--- Fase 2: Capacidad y Parametros ---")
    p = ber_final
    px0 = trama_larga.count("0") / len(trama_larga)
    px1 = 1.0 - px0

    py0 = px0 * (1 - p) + px1 * p
    py1 = px0 * p + px1 * (1 - p)

    hy = H(py0)
    hy_x = H(p)
    ixy = hy - hy_x
    capacidad = 1.0 - hy_x

    print(f"Probabilidad de error (p): {p:.6f}")
    print(f"Matriz P(Y|X):\n  P(Y=0|X=0)={1-p:.4f}  P(Y=1|X=0)={p:.4f}\n  P(Y=0|X=1)={p:.4f}  P(Y=1|X=1)={1-p:.4f}")
    print(f"P(X=0): {px0:.4f} | P(X=1): {px1:.4f}")
    print(f"Informacion Mutua I(X;Y): {ixy:.6f} bits/simbolo")
    print(f"Capacidad de Canal (C)  : {capacidad:.6f} bits/símbolo")

    enviar_mensaje(sock, "SALIR")
    sock.close()

# --- Análisis de Maximización ---
# ¿Logró su mensaje maximizar la capacidad del canal?
# Sí, en la prueba con 1.000.000 bits aleatorios la fuente es equiprobable (P(X=0) ≈ P(X=1) ≈ 0.5),
# por lo que H(Y) alcanza 1.0 bit y la información mutua I(X;Y) iguala a la Capacidad C.
# En cambio, si enviamos solo texto ASCII, la trama presenta sesgo hacia ceros (ej. bits de control),
# reduciendo H(Y) y haciendo que I(X;Y) sea menor que C. Para maximizar C, la fuente debe ser equiprobable.

if __name__ == "__main__":
    main()
