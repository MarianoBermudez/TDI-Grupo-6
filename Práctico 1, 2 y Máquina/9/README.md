#### Simulación cliente-servidor mediante Sockets TCP para estimar el BER y calcular la capacidad de canal.

## Archivos
- `servidor_bsc.py`: Servidor que simula el canal BSC (puerto 5555).
- `cliente_bsc.py`: Cliente que realiza las pruebas empíricas de BER, envío de texto y cálculo de capacidad.

## Ejecución

1. Iniciar el servidor en una terminal:
```bash
python servidor_bsc.py
```

2. En otra terminal, ejecutar el cliente:
```bash
python cliente_bsc.py
```

## Salida esperada
- BER empírico para tramas de 100, 10.000 y 1.000.000 bits.
- Demostración de texto ruidoso en recepción.
- Matriz de transición $P(Y|X)$, información mutua $I(X;Y)$ y capacidad $C = 1 - H(p)$.
