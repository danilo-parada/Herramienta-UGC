filepath = r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py'

with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Eliminar líneas 3174 a 3190 (índices 3173 a 3189)
# Estas son las líneas del código viejo duplicado

print(f"Total líneas antes: {len(lines)}")
print(f"Línea 3174: {lines[3173][:60]}")
print(f"Línea 3175: {lines[3174][:60]}")
print(f"Línea 3190: {lines[3189][:60]}")

# Eliminar desde línea 3174 (índice 3173) hasta 3190 (índice 3189) inclusive
del lines[3173:3190]

print(f"Total líneas después: {len(lines)}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Líneas eliminadas correctamente")
