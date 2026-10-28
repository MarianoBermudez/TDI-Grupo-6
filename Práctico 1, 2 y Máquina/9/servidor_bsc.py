import socket
import random
import struct
import threading

HOST = "0.0.0.0"
PUERTO = 5555
SEMILLA_CANAL = 2026

rng_canal = random.Random(SEMILLA_CANAL)
limite_a = rng_canal.random()
limite_b = rng_canal.random()
P_ERROR = min(limite_a, limite_b) * rng_canal.random()

def recibir_exactamente(sock, cantidad):
    datos = bytearray()
    while len(datos) < cantidad:
        bloque = sock.recv(cantidad - len(datos))
        if not bloque:
            raise ConnectionError("Conexión cerrada.")
        datos.extend(bloque)
    return bytes(datos)

def recibir_mensaje(sock):
    encabezado = recibir_exactamente(sock, 4)
    longitud = struct.unpack("!I", encabezado)[0]
    datos = recibir_exactamente(sock, longitud)
    return datos.decode("ascii")

def enviar_mensaje(sock, mensaje):
    datos = mensaje.encode("ascii")
    encabezado = struct.pack("!I", len(datos))
    sock.sendall(encabezado + datos)

def atender_cliente(cliente, direccion):
    rng_ruido = random.Random(SEMILLA_CANAL + 1)
    try:
        while True:
            mensaje = recibir_mensaje(cliente)
            if mensaje == "SALIR":
                break
            if not mensaje:
                enviar_mensaje(cliente, "ERROR: mensaje vacio")
                continue
            if any(bit not in "01" for bit in mensaje):
                enviar_mensaje(cliente, "ERROR: solo bits 0 y 1")
                continue
            
            salida = []
            for bit in mensaje:
                if rng_ruido.random() < P_ERROR:
                    salida.append("1" if bit == "0" else "0")
                else:
                    salida.append(bit)
            enviar_mensaje(cliente, "".join(salida))
    except (ConnectionError, OSError):
        pass
    finally:
        cliente.close()

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen()
    print(f"Servidor BSC escuchando en puerto {PUERTO}...")
    try:
        while True:
            cliente, direccion = servidor.accept()
            threading.Thread(target=atender_cliente, args=(cliente, direccion), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.close()

if __name__ == "__main__":
    iniciar_servidor()
