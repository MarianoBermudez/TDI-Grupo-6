from math import isqrt

# Algoritmo de Fermat: busca n = a² - b² = (a-b)(a+b)
def fermat(n):
    a = isqrt(n)
    if a * a < n:
        a += 1
    encontrado = False         
    while not encontrado:
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:        
            encontrado = True
        else:
            a += 1
    return a - b, a + b

# Factoriza n y obtiene la clave privada d a partir de la clave pública (n, e)
def calcular_clave_privada(n, e):
    p, q = fermat(n)
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)          # inverso modular de e
    return p, q, d

if __name__ == "__main__":
    # Ejercicio 13
    n, e, c = 2291, 17, 575
    p, q, d = calcular_clave_privada(n, e)
    m = pow(c, d, n)             # M = C^d mod n
    print("\nEjercicio 13:")
    print(f"p = {p}, q = {q}")
    print(f"d = {d}")
    print(f"Mensaje descifrado = {m} -> '{chr(m)}'")

    # Ejercicio 14
    n, e = 536813567, 3602561
    p, q, d = calcular_clave_privada(n, e)
    print("\nEjercicio 14")
    print(f"p = {p}, q = {q}")
    print(f"d = {d}")