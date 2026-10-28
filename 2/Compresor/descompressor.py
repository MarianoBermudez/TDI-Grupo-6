import os
import struct
import sys
import time
import heapq

class NodoHuffman:
    frec: int
    simbolo: bytes
    izq: object
    der: object
    def __init__(self, frec, simbolo=None, izq=None, der=None):
        self.frec = frec
        self.simbolo = simbolo
        self.izq = izq
        self.der = der
    def __lt__(self, otro):
        return self.frec < otro.frec

def deserializar_arbol(bits, pos):
    #Inversa de serializar_arbol: lee el preorden desde 'pos'.
    #"1" -> hoja (los siguientes 8 bits son el simbolo) ; "0" -> nodo interno (izq y der a continuacion).
    #Devuelve (nodo, nueva_posicion).
    if pos >= len(bits):
        raise ValueError("arbol truncado")
    if bits[pos] == "1":
        if pos + 9 > len(bits):
            raise ValueError("arbol truncado")
        return NodoHuffman(0, int(bits[pos+1:pos+9], 2)), pos + 9
    izq, pos = deserializar_arbol(bits, pos + 1)
    der, pos = deserializar_arbol(bits, pos)
    return NodoHuffman(0, izq=izq, der=der), pos

def bwt_inversa(bwt_bytes, indice_primario):
    try:
        n = len(bwt_bytes)
        if n == 0: return bytearray()
        
        #conteo de apariciones de cada byte
        conteo = [0] * 256
        for b in bwt_bytes:
            conteo[b] += 1
        
        #inicio de cada byte en el orden alfabetico
        inicios = [0] * 256
        total = 0
        for i in range(256):
            inicios[i] = total
            total += conteo[i]
        
        #vector LF, es un vector que indica la posicion del siguiente caracter en la BWT
        vector_lf = [0] * n
        for i, b in enumerate(bwt_bytes):
            vector_lf[inicios[b]] = i
            inicios[b] += 1
        
        #reconstruye el archivo original usando el vector LF
        salida = bytearray(n)
        actual = vector_lf[indice_primario]
        for i in range(n):
            salida[i] = bwt_bytes[actual]
            actual = vector_lf[actual]
            
        return salida
    except IndexError:
        print("[ERROR] Índice BWT fuera de rango. El archivo está corrupto.")
        sys.exit(1)
    except MemoryError:
        print("[ERROR] Memoria insuficiente para reconstruir el archivo.")
        sys.exit(1)

def descomprimir(archivo_in, archivo_out):
    try:
        #Abre el archivo y lee la cabecera
        with open(archivo_in, "rb") as f_in:
            magic = f_in.read(4)
            #Verifica que el archivo sea valido
            if magic != b"STA2":
                print("[ERROR] Firma de archivo inválida. No es un archivo STA2 válido.")
                sys.exit(1)
            #Lee el indice primario
            indice_bwt = struct.unpack(">I", f_in.read(4))[0]
            #Lee los bits faltantes
            faltan = struct.unpack(">B", f_in.read(1))[0]
            #Lee el payload
            payload = f_in.read()
        #Convierte el payload a bits
        bits = "".join(f"{byte:08b}" for byte in payload)
        #Elimina los bits faltantes
        if faltan > 0:
            bits = bits[:-faltan]
        
        #Reconstruye el arbol que viaja al comienzo del flujo de bits
        try:
            raiz, pos = deserializar_arbol(bits, 0)
        except (ValueError, RecursionError):
            print("[ERROR] Árbol de Huffman corrupto o truncado.")
            sys.exit(1)

        #Decodifica el resto de los bits usando ese arbol
        bwt_bytes = bytearray()
        nodo_actual = raiz
        for bit in bits[pos:]:
            nodo_actual = nodo_actual.izq if bit == "0" else nodo_actual.der
            if nodo_actual.simbolo is not None:
                bwt_bytes.append(nodo_actual.simbolo)
                nodo_actual = raiz
        #Invierte el BWT      
        datos_originales = bwt_inversa(bwt_bytes, indice_bwt)
        #Escribe el archivo original
        with open(archivo_out, "wb") as f_out:
            f_out.write(datos_originales)
    #Manejo de errores
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {archivo_in}")
        sys.exit(1)
    except struct.error:
        print("[ERROR] Cabecera corrupta o tamaño de archivo incorrecto.")
        sys.exit(1)
    except PermissionError:
        print("[ERROR] Permisos denegados para leer o escribir los archivos.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR CRÍTICO] Ocurrió un fallo inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python descompresor.py <entrada> <salida>")
        sys.exit(1)
        
    archivo_in = sys.argv[1]
    archivo_out = sys.argv[2]
    
    if not os.path.exists(archivo_in) or os.path.getsize(archivo_in) == 0:
        print(f"[ERROR] Archivo inválido o vacío: {archivo_in}")
        sys.exit(1)
        
    try:
        t_inicio = time.perf_counter()
        descomprimir(archivo_in, archivo_out)
        tiempo_ms = (time.perf_counter() - t_inicio) * 1000
        
        size_d = os.path.getsize(archivo_out)
        
        print(f"--- DESCOMPRESIÓN EXITOSA ---")
        print(f"Archivo comprimido: {archivo_in}")
        print(f"Archivo reconstruido:{archivo_out}")
        print(f"Tamaño resultante:  {size_d} B")
        print(f"Tiempo de ejecución:{tiempo_ms:.2f} ms")
    except KeyboardInterrupt:
        print("\n[INFO] Descompresión cancelada por el usuario.")
        sys.exit(0)