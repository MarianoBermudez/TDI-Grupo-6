def calcular_digito_verificador(cuit):
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = 0
    for i in range(10):
        suma += int(cuit[i]) * pesos[i]
    resto = suma % 11
    digito = 11 - resto
    if digito == 11:
        digito = 0
    elif digito == 10:
        digito = -1
    return digito

def validar_cuit(cuit):
    if len(cuit) != 11:
        return False
    for caracter in cuit:
        if not caracter.isdigit():
            return False
    digito_calculado = calcular_digito_verificador(cuit)
    digito_ingresado = int(cuit[10])
    if digito_calculado == -1:
        return False
    return digito_calculado == digito_ingresado

def main():
    print("VALIDACIÓN DE CUIT/CUIL")
    cuit = input("Ingrese un CUIT/CUIL de 11 dígitos: ")
    if validar_cuit(cuit):
        print("El CUIT/CUIL ingresado es Válido.")
    else:
        print("El CUIT/CUIL ingresado es Inválido.")

if __name__ == "__main__":
    main()