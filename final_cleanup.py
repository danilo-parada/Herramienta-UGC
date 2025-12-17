filepath = r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py'

with open(filepath, 'rb') as f:
    content = f.read()

# Buscar el patrón del código viejo (usando bytes para evitar problemas de encoding)
# Buscar desde "st.markdown("---")" con indentación incorrecta hasta el segundo "st.markdown("---")"

# Convertir a string con errores de encoding reemplazados
text = content.decode('utf-8', errors='replace')

# Dividir en líneas
lines = text.split('\n')

# Encontrar y eliminar el bloque problemático
output_lines = []
skip_mode = False
skip_count = 0

for i, line in enumerate(lines):
    # Detectar inicio del bloque malo (línea con st.markdown("---") seguida de indentación incorrecta)
    if i > 3170 and 'st.markdown("---")' in line and not skip_mode:
        # Verificar si la siguiente línea tiene indentación incorrecta (8 espacios cuando debería tener 4)
        if i + 1 < len(lines) and lines[i+1].startswith('        if st.button'):
            skip_mode = True
            output_lines.append(line)  # Mantener el st.markdown("---")
            continue
    
    # Si estamos en modo skip, contar hasta encontrar el siguiente st.markdown("---")
    if skip_mode:
        if 'st.markdown("---")' in line:
            skip_mode = False
            # No agregar esta línea (ya tenemos el---" anterior)
            continue
        else:
            # Saltar esta línea
            continue
    
    # Línea normal, agregarla
    output_lines.append(line)

# Unir de nuevo
new_text = '\n'.join(output_lines)

# Guardar
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_text)

print(f"✅ Procesado. Total líneas originales: {len(lines)}, nuevas: {len(output_lines)}")
