# Script temporal para arreglar emoji corrupto en IRL

# Leer el archivo
with open(r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar y reemplazar la línea con el bot��n corrupto
for i, line in enumerate(lines):
    if 'Cargar respuestas al sistema' in line and 'use_container_width' in line:
        lines[i] = '        if st.button("✅ Aplicar respuestas al sistema", use_container_width=True, type="primary"):\n'
        print(f'Línea {i+1} reemplazada')
        break

# Guardar el archivo
with open(r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Archivo actualizado correctamente')
