filepath = r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py'

# Leer
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Buscar la línea problemática (línea 3176 aproximadamente)
found = False
for i in range(len(lines)):
    # Buscar línea con if st.button y el emoji corrupto
    if 'st.button' in lines[i] and 'Cargar respuestas al sistema' in lines[i] and i > 3170:
        print(f"Encontrado en línea {i+1}")
        
        # Encontrar el final del bloque (la línea con st.rerun())
        end = i
        while end < len(lines) and 'st.rerun()' not in lines[end]:
            end += 1
        end += 1  # Incluir la línea st.rerun()
        
        # Eliminar estas líneas problemáticas (desde la línea del if hasta st.rerun())
        # Retroceder para eliminar también la indentación incorrecta
        start = i
        while start > 0 and lines[start-1].strip() == '':
            start -= 1
        
        # Retroceder más para eliminar el if mal indentado
        if start > 0 and lines[start].startswith('        if st.button'):
            start -= 1  # Eliminar la línea vacía antes también
        
        print(f"Eliminando líneas {start+1} a {end+1}")
        
        # Eliminar las líneas
        del lines[start:end]
        
        found = True
        break

if found:
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Código viejo eliminado correctamente")
else:
    print("❌ No se encontró el código a eliminar")
