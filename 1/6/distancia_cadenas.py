def distancia_hamming(cadena1, cadena2):
    if len(cadena1) != len(cadena2):
        return -1
    distancia = 0
    for i in range(len(cadena1)):
        if cadena1[i] != cadena2[i]:
            distancia += 1
    return distancia

def distancia_levenshtein(cadena1, cadena2):
    filas = len(cadena1) + 1
    columnas = len(cadena2) + 1
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(0)
        matriz.append(fila)
    #Primera columna: Representa las eliminaciones necesarias
    for i in range(filas):
        matriz[i][0] = i
    #Primera fila: Representa las inserciones necesarias
    for j in range(columnas):
        matriz[0][j] = j
    # Completar la matriz
    for i in range(1, filas):
        for j in range(1, columnas):
            #Si los caracteres son iguales no necesitamos realizar una sustitución.
            if cadena1[i - 1] == cadena2[j - 1]:
                costo = 0
            else:
                costo = 1
            #Elegimos la operación que tenga el menor costo.
            matriz[i][j] = min(
                matriz[i - 1][j] + 1,       #Eliminación
                matriz[i][j - 1] + 1,       #Inserción
                matriz[i - 1][j - 1] + costo  #Sustitución
            )
    return matriz[-1][-1]

def grado_similitud(cadena1, cadena2):
    distancia = distancia_levenshtein(cadena1, cadena2)
    longitud_maxima = max(len(cadena1), len(cadena2))
    if longitud_maxima == 0:
        return 100
    similitud = (1 - distancia / longitud_maxima) * 100
    return similitud

def comparar_cadenas():
    print("COMPARACIÓN DE CADENAS")
    cadena1 = input("Ingrese la primera cadena: ")
    cadena2 = input("Ingrese la segunda cadena: ")
    print("RESULTADOS")
    hamming = distancia_hamming(cadena1, cadena2)
    if hamming == -1:
        print("Distancia de Hamming:")
        print("No se puede calcular.Las cadenas tienen distinta longitud.")
    else:
        print("Distancia de Hamming:", hamming)
    levenshtein = distancia_levenshtein(cadena1, cadena2)
    print("Distancia de Levenshtein:", levenshtein)
    similitud = grado_similitud(cadena1, cadena2)
    print("Grado de similitud:", round(similitud, 2),"%")

if __name__ == "__main__":    
    comparar_cadenas()
