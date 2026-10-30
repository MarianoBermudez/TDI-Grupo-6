# Ejercicio 15a: Se muestra como funciona el algoritmo de exponenciación binaria
def potencia_mod(x, m, n):
    resultado = 1
    x = x % n
    while m > 0:
        if m % 2 == 1:           # bit en 1
            resultado = (resultado * x) % n
        x = (x * x) % n          # elevar al cuadrado
        m //= 2
    return resultado

# Ejercicio 15b: Se muestra como funciona el algoritmo división por tentativa
def factorizar(N):
    factores = []
    f = 2
    while f * f <= N:
        while N % f == 0:
            factores.append(f)
            N //= f
        f += 1
    if N > 1:
        factores.append(N)
    return factores

if __name__ == "__main__":
    print("\nEjercicio 15a: ")
    print(f"575^257 mod 2291 = {potencia_mod(575, 257, 2291)}")   

    print("\nEjercicio 15b:")
    print(f"Factores de 2291 = {factorizar(2291)}")            