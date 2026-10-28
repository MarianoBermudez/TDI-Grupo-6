### Resultados Obtenidos:
- Archivo JSON (Texto variable) : 7,425 bytes
- Archivo BIN  (Bitwise fijo)   : 2,100 bytes
- Ahorro de espacio obtenido    : 71.72% (Relación 3.54:1)

### Conclusión:
El formato JSON introduce una alta **redundancia sintáctica** al repetir claves, comillas y cadenas ASCII. La codificación **Bitwise** elimina totalmente este sobrecosto al empaquetar **8 campos booleanos en 1 único byte** (1 bit por estado).

En **sistemas de alta escala** (millones de registros), la elección de codificaciones binarias optimizadas reduce drásticamente los costos de almacenamiento, optimiza el ancho de banda en transmisiones de red y disminuye los tiempos de lectura/escritura (I/O).