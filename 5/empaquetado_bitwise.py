import os
import json
import struct

FLAG_NAMES = [
    "Estudios_Primarios",
    "Estudios_Secundarios",
    "Estudios_Universitarios",
    "Vivienda_Propia",
    "Obra_Social",
    "Trabaja",
    "Vehiculo_Propio",
    "Licencia_Conducir"
]

def generate_sample_data():
    personas = []
    nombres = [
        "Perez Juan Carlos", "Gomez Maria Elena", "Lopez Carlos Alberto", "Rodriguez Ana Sofia", "Fernandez Luis Mateo",
        "Diaz Sofia Valentina", "Martinez Diego Nicolas", "Alvarez Elena Isabel", "Romero Javier Martin", "Torres Lucia Camila",
        "Sosa Mateo Benjamin", "Benitez Camila Agustina", "Ruiz Nicolas Gabriel", "Flores Valentina Paz", "Acosta Martin Ignacio",
        "Medina Isabel Victoria", "Herrera Lucas Emanuel", "Castro Paula Daniela", "Gimenez Joaquin Tomas", "Vazquez Martina Sol"
    ]
    direcciones = [
        "Av. Corrientes 1234", "Calle 50 Nro 432", "San Martin 850", "Belgrano 210", "Mitre 1500",
        "Rivadavia 3400", "Urquiza 920", "Sarmiento 110", "Alvear 560", "Pueyrredon 780",
        "Lavalle 1420", "Cordoba 2300", "Santa Fe 3100", "Cabildo 1850", "Callao 940",
        "Maipu 430", "Florida 670", "Alsina 1290", "Moreno 840", "Defensa 350"
    ]
    
    for i in range(20):
        dni = 30000000 + (i * 412357) % 15000000
        univ = (i % 3 == 0)
        sec = univ or (i % 2 == 0)
        prim = True  # Todos tienen primario en este conjunto
        
        vehiculo = (i % 4 == 0)
        licencia = vehiculo or (i % 2 == 0)
        
        flags = [
            prim,                       # Bit 0: Primarios
            sec,                        # Bit 1: Secundarios
            univ,                       # Bit 2: Universitarios
            (i % 5 == 0),               # Bit 3: Vivienda Propia
            (i % 2 != 0),               # Bit 4: Obra Social
            (i % 3 != 1),               # Bit 5: Trabaja
            vehiculo,                   # Bit 6: Vehículo Propio
            licencia                    # Bit 7: Licencia de Conducir
        ]
        
        personas.append({
            "Nombre": nombres[i],
            "Direccion": direcciones[i],
            "DNI": dni,
            "flags": flags
        })
    return personas

# OPERACIONES DE EMPAQUETADO BITWISE
def pack_flags_bitwise(flags_input):
    """
    Empaqueta 8 booleanos en 1 único byte (uint8) usando operadores Bitwise (OR '|' y Shift Left '<<').
    Acepta tanto una lista de 8 booleanos como un diccionario de campos booleanos.
    """
    byte_val = 0
    
    if isinstance(flags_input, (list, tuple)):
        bool_list = flags_input
    elif isinstance(flags_input, dict):
        # Extraer los 8 booleanos según FLAG_NAMES o buscando variaciones
        bool_list = []
        for name in FLAG_NAMES:
            val = flags_input.get(name)
            if val is None:
                # Probar variaciones sin guion bajo o minusculas
                val = flags_input.get(name.replace("_", " ")) or flags_input.get(name.lower())
            
            # Convertir string "True"/"False"/"S"/"N" o bool a booleano real
            if isinstance(val, str):
                bool_list.append(val.strip().lower() in ("true", "s", "1", "si", "sí"))
            else:
                bool_list.append(bool(val))
    else:
        raise ValueError("El parámetro de flags debe ser una lista de booleanos o un diccionario.")
        
    for i, flag in enumerate(bool_list[:8]):
        if flag:
            byte_val |= (1 << i)
            
    return byte_val

def unpack_flags_bitwise(byte_val):
    """
    Desempaqueta 1 byte en 8 booleanos usando operadores Bitwise (AND '&' y Shift Right '>>').
    Retorna una lista de 8 valores booleanos (True/False).
    """
    return [((byte_val >> i) & 1) == 1 for i in range(8)]

# FORMATO BINARIO Y ARCHIVOS (JSON & BIN)
# Estructura del registro binario de longitud fija (105 bytes):
# 50s : Nombre (50 bytes, string codificado UTF-8)
# 50s : Dirección (50 bytes, string codificado UTF-8)
# I   : DNI (4 bytes, unsigned int de 32 bits)
# B   : Flags empaquetados (1 byte, unsigned char / 8 bits)
STRUCT_FORMAT = '<50s50sIB'
RECORD_SIZE = struct.calcsize(STRUCT_FORMAT)  # Exactamente 105 bytes

def save_json(filepath, personas):
    """Guarda los datos en formato JSON de longitud variable."""
    records = []
    for p in personas:
        # Obtener campos tolerando claves en mayúsculas o minúsculas
        nombre = p.get("Nombre") or p.get("nombre", "")
        direccion = p.get("Direccion") or p.get("direccion", "")
        dni = p.get("DNI") or p.get("dni", 0)
        
        rec = {
            "Nombre": nombre,
            "Direccion": direccion,
            "DNI": dni
        }
        
        # Extraer lista de booleanos
        flags = p.get("flags") or p.get("Flags")
        if flags is None:
            flags = [p.get(name, False) for name in FLAG_NAMES]
            
        for idx, fname in enumerate(FLAG_NAMES):
            rec[fname] = "True" if flags[idx] else "False"
            
        records.append(rec)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def read_json(filepath):
    """Lee el archivo JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_binary(filepath, personas):
    """Guarda los datos en un archivo binario optimizado de longitud fija."""
    with open(filepath, 'wb') as f:
        for p in personas:
            nombre = p.get("Nombre") or p.get("nombre", "")
            direccion = p.get("Direccion") or p.get("direccion", "")
            dni = p.get("DNI") or p.get("dni", 0)
            
            # Obtener los 8 booleanos tolerando cualquier formato de clave ('flags', 'Flags' o campos individuales)
            flags_input = p.get("flags")
            if flags_input is None:
                flags_input = p.get("Flags")
            if flags_input is None:
                flags_input = p  # Pasar el diccionario directamente
                
            flags_byte = pack_flags_bitwise(flags_input)
            
            nombre_bytes = nombre.encode('utf-8')[:50].ljust(50, b'\x00')
            dir_bytes = direccion.encode('utf-8')[:50].ljust(50, b'\x00')
            
            packed_record = struct.pack(STRUCT_FORMAT, nombre_bytes, dir_bytes, dni, flags_byte)
            f.write(packed_record)

def read_binary(filepath):
    """Lee el archivo binario y desempaqueta el byte de booleanos con Bitwise."""
    personas = []
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(RECORD_SIZE)
            if not chunk or len(chunk) < RECORD_SIZE:
                break
            nombre_bytes, dir_bytes, dni, flags_byte = struct.unpack(STRUCT_FORMAT, chunk)
            nombre = nombre_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
            direccion = dir_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
            
            flags_bool = unpack_flags_bitwise(flags_byte)
            
            # Crear diccionario con la lista desempaquetada y campos individuales
            p_dict = {
                "Nombre": nombre,
                "Direccion": direccion,
                "DNI": dni,
                "flags_byte": flags_byte,
                "flags": flags_bool
            }
            for idx, fname in enumerate(FLAG_NAMES):
                p_dict[fname] = flags_bool[idx]
                
            personas.append(p_dict)
    return personas


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "personas.json")
    bin_path = os.path.join(base_dir, "personas.bin")
    
    # 1. Generar datos y guardar ambos archivos
    sample_personas = generate_sample_data()
    save_json(json_path, sample_personas)
    save_binary(bin_path, sample_personas)
    
    # 2. Leer y verificar recíprocamente
    datos_json = read_json(json_path)
    datos_bin = read_binary(bin_path)
    
    print("COMPARACIÓN DE TAMAÑOS Y EFICIENCIA DE ALMACENAMIENTO")
    json_size = os.path.getsize(json_path)
    bin_size = os.path.getsize(bin_path)
    ahorro_pct = (1 - (bin_size / json_size)) * 100
    
    print(f"• Archivo JSON (Texto variable) : {json_size:,} bytes")
    print(f"• Archivo BIN  (Bitwise fijo)   : {bin_size:,} bytes")
    print(f"• Ahorro de espacio obtenido    : {ahorro_pct:.2f}% (Relación {json_size/bin_size:.2f}:1)")