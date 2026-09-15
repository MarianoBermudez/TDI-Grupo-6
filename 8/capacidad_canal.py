import math

def calcular_entropia(probabilidades):
    return sum(-p * math.log2(p) for p in probabilidades if p > 0)

def main():
    matriz_canal = []
    print("Ingrese las probabilidades condicionales P(Y|X) para la matriz 2x4.")
    print("Use espacios para separar los 4 valores de cada fila.\n")
    
    # 1. Ingreso y validación de la Matriz del Canal utilizando variables de control
    for i in range(2):
        fila_valida = False
        while not fila_valida:
            try:
                entrada = input(f"Fila {i} correspondientes a P(Y|X={i}): ").split()
                
                if len(entrada) != 4:
                    print("Error: Se requieren exactamente 4 valores.")
                else:   
                    fila = [float(x) for x in entrada]
                    suma_fila = sum(fila)
                    
                    if not suma_fila == 1:
                        print(f"Error: La suma de las probabilidades es {suma_fila:.4f}. Debe ser estrictamente 1.0.")
                    else:
                        matriz_canal.append(fila)
                        fila_valida = True
                        
            except ValueError:
                print("Error: Todos los valores deben ser numéricos.")

    # Entropías condicionales de cada fila
    h_y_dado_x0 = calcular_entropia(matriz_canal[0])
    h_y_dado_x1 = calcular_entropia(matriz_canal[1])

    capacidad_C = -1.0
    optimo_px0 = 0.0
    optimo_px1 = 0.0

    # 2. Búsqueda Exhaustiva (saltos de 0.01)
    for i in range(101):
        px0 = i / 100.0
        px1 = 1.0 - px0

        # 3. Cálculo de Información Mutua
        py = [0.0] * 4
        for j in range(4):
            py[j] = (px0 * matriz_canal[0][j]) + (px1 * matriz_canal[1][j])

        h_y = calcular_entropia(py)
        h_y_dado_x = (px0 * h_y_dado_x0) + (px1 * h_y_dado_x1)
        i_x_y = h_y - h_y_dado_x

        # 4. Maximización
        if i_x_y > capacidad_C:
            capacidad_C = i_x_y
            optimo_px0 = px0
            optimo_px1 = px1

    # 5. Salida de resultados
    print("\n--- Resultados ---")
    print(f"Capacidad de Canal (C):       {capacidad_C:.6f} bits/símbolo")
    print(f"Distribución óptima de P(X):  P(X=0) = {optimo_px0:.2f} | P(X=1) = {optimo_px1:.2f}")

if __name__ == "__main__":
    main()