#### Validación de CUIT/CUIL:

Programa en Python que valida un CUIT/CUIL utilizando el algoritmo de Módulo 11 para calcular y verificar el dígito de control.

#### Funcionamiento:

El programa solicita un CUIT/CUIL de 11 dígitos y realiza:

- Verificación de longitud y caracteres numéricos.

- Cálculo del dígito verificador mediante el algoritmo de Módulo 11.

- Comparación entre el dígito calculado y el ingresado.

- Determinación de si el CUIT/CUIL es válido o inválido.

#### Algoritmo Módulo 11:

Para calcular el dígito verificador se toman los primeros 10 dígitos y se multiplican por los pesos:

- 5, 4, 3, 2, 7, 6, 5, 4, 3, 2.

Luego se suman todos los resultados y se calcula el resto de dividir esa suma por 11. El dígito verificador se obtiene realizando:
`11 - resto`

Si el resultado es 11, se utiliza 0. Si el resultado es 10, el CUIT/CUIL se considera inválido.

#### Ejemplo

CUIT/CUIL ingresado: 20-12345678-6

Cálculo:

`2×5 + 0×4 + 1×3 + 2×2 + 3×7 + 4×6 + 5×5 + 6×4 + 7×3 + 8×2 = 148`

`148 % 11 = 5`

`11 - 5 = 6`

Resultados:

- Dígito verificador calculado: 6

- Dígito verificador ingresado: 6

- Resultado: Válido
