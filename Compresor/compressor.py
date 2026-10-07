import os
import struct
import sys
import time
import heapq
from collections import Counter

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
#Basicamente -> creacion de un arbol como en EDA

def construir_arbol(frecuencias):
    #Pasada 1 ya hecha: 'frecuencias' son las del archivo real {byte: cantidad}.
    #Solo entran al arbol los bytes que aparecen (frecuencia > 0).
    heap = [NodoHuffman(frec, simb) for simb, frec in frecuencias.items() if frec > 0]
    if len(heap) == 1:
        #Caso borde: un unico simbolo distinto (ej. "aaaa...") -> el arbol seria una sola hoja
        #y su codigo tendria 0 bits. Se agrega una hoja ficticia para forzar un codigo de 1 bit.
        unico = heap[0].simbolo
        heap.append(NodoHuffman(0, (unico + 1) % 256))
    heapq.heapify(heap)
    while len(heap) > 1:
        izq = heapq.heappop(heap)
        der = heapq.heappop(heap)
        heapq.heappush(heap, NodoHuffman(izq.frec + der.frec, izq=izq, der=der))
    return heap[0]

def generar_codigos(raiz):
    codigos = {}
    def generar(nodo, prefijo=""):
        if nodo.simbolo is not None:
            codigos[nodo.simbolo] = prefijo
        else:
            generar(nodo.izq, prefijo + "0")
            generar(nodo.der, prefijo + "1")
    generar(raiz)
    return codigos

def serializar_arbol(nodo):
    #Recorrido en preorden: nodo interno -> "0" ; hoja -> "1" + simbolo en 8 bits.
    #Con k hojas hay (k-1) nodos internos: 9*k + (k-1) = 10k - 1 bits en total (k=76 -> 95 B ; k=256 -> 320 B).
    if nodo.simbolo is not None:
        return "1" + f"{nodo.simbolo:08b}"
    return "0" + serializar_arbol(nodo.izq) + serializar_arbol(nodo.der)

def bwt_directa(bloque_bytes):
    #busca hacer las rotaciones lo que hace es que por ejemplo a la palabra CASA
    #le guarda el doble es decir CASACASA, entonces luego obtiene las rotaciones 
    #por medio del indice i, es decir para i=0 es CASA, para i=1 es ACAS, para i=2 es SACA, para i=3 es ACAS
    #Como sabe hasta donde por la n que se obtiene al principio, asi es como obtiene las rotaciones
    try:
        n = len(bloque_bytes)
        doble = bytes(bloque_bytes) + bytes(bloque_bytes)
        sa = sorted(range(n), key=lambda i: doble[i:i+n]) #<- construccion del arreglo de sufijos ordenado
        bwt_bytes = bytearray(doble[i - 1] for i in sa) #cuando i=0 es doble[-1] pero esto indica el ultimo caracter de los sufijos ordenados
        #en bwt_bytes es la secuencia de bytes transformada de bwt
        return bwt_bytes, sa.index(0)
    except MemoryError:
        print("[ERROR] Memoria insuficiente para calcular BWT. El archivo es demasiado grande.")
        sys.exit(1)

def comprimir(archivo_in, archivo_out):
    try:
        with open(archivo_in, "rb") as f_in:
            datos = f_in.read()
        
        if not datos:
            print("[ERROR] Archivo vacío.")
            sys.exit(1)

        bwt_bytes, indice_bwt = bwt_directa(datos)
        
        #Pasada 1: contar frecuencias reales. Pasada 2: codificar con el arbol resultante.
        raiz = construir_arbol(Counter(bwt_bytes))
        codigos = generar_codigos(raiz)
        arbol_bits = serializar_arbol(raiz) #<- el arbol viaja en el archivo (no las frecuencias)

        bits = arbol_bits + "".join(codigos[b] for b in bwt_bytes)
        faltan = (8 - (len(bits) % 8)) % 8 #Se usa para rellenar los ultimos bits con ceros para que sean multiplos de 8, es decir un numero exacto de bytes
        bits += "0" * faltan
        
        payload = bytearray(int(bits[i:i+8], 2) for i in range(0, len(bits), 8)) #Convierte los bits a bytes
        
        with open(archivo_out, "wb") as f_out:
            f_out.write(b"STA2") #<- Marca de archivo (STA2 = Huffman con arbol en cabecera)
            f_out.write(struct.pack(">I", indice_bwt)) #<- Indice de BWT
            f_out.write(struct.pack(">B", faltan)) #<- Cantidad de bits de padding
            f_out.write(payload) #<- Arbol serializado + payload comprimido (mismo flujo de bits)
            
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {archivo_in}")
        sys.exit(1)
    except PermissionError:
        print("[ERROR] Permisos denegados para leer o escribir los archivos.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR CRÍTICO] Ocurrió un fallo inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python compresor.py <entrada> <salida>")
        sys.exit(1)
        
    archivo_in = sys.argv[1]
    archivo_out = sys.argv[2]
    
    if not os.path.exists(archivo_in) or os.path.getsize(archivo_in) == 0:
        print(f"[ERROR] Archivo inválido o vacío: {archivo_in}")
        sys.exit(1)
        
    try:
        t_inicio = time.perf_counter()
        comprimir(archivo_in, archivo_out)
        tiempo_ms = (time.perf_counter() - t_inicio) * 1000
        
        size_o = os.path.getsize(archivo_in)
        size_c = os.path.getsize(archivo_out)
        ratio = size_o / size_c if size_c > 0 else 0
        ahorro = (1 - size_c / size_o) * 100 if size_o > 0 else 0
        
        print(f"--- COMPRESIÓN EXITOSA ---")
        print(f"Archivo de entrada: {archivo_in}")
        print(f"Archivo de salida:  {archivo_out}")
        print(f"Tamaño original:    {size_o} B")
        print(f"Tamaño comprimido:  {size_c} B")
        print(f"Ratio de compresión:{ratio:.3f}")
        print(f"Ahorro de espacio:  {ahorro:.2f}%")
        print(f"Tiempo de ejecución:{tiempo_ms:.2f} ms")
        print(f"Parámetro principal: BWT + Huffman estático de doble pasada (árbol en cabecera)")
    except KeyboardInterrupt:
        print("\n[INFO] Compresión cancelada por el usuario.")
        sys.exit(0)