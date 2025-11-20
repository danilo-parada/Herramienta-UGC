import re

filepath = r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py'

# Leer el archivo
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Encontrar la línea con col_aplicar
for i in range(len(lines)):
    if 'col_aplicar, col_cancelar = st.columns([1, 1])' in lines[i]:
        print(f"Encontrada línea {i+1}: {lines[i].strip()}")
        
        # Las próximas líneas hasta st.markdown("---") deben ser reemplazadas
        # Encontrar el final (la línea con st.markdown("---"))
        end_idx = i + 1
        while end_idx < len(lines) and 'st.markdown("---")' not in lines[end_idx]:
            end_idx += 1
        
        print(f"Reemplazando desde línea {i+1} hasta {end_idx+1}")
        
        # Crear el nuevo bloque
        indent = '        '
        new_lines = [
            lines[i],  # Mantener la línea de col_aplicar
            '\n',
            f'{indent}with col_aplicar:\n',
            f'{indent}    if st.button("✅ Aplicar respuestas al sistema", use_container_width=True, type="primary"):\n',
            f'{indent}        # Aplicar todas las respuestas al session_state\n',
            f'{indent}        for key, value in st.session_state.pending_irl_responses.items():\n',
            f'{indent}            st.session_state[key] = value\n',
            f'{indent}        \n',
            f'{indent}        # Marcar como aplicado\n',
            f'{indent}        st.session_state.irl_responses_applied = True\n',
            f'{indent}        \n',
            f'{indent}        # Limpiar pendientes pero mantener datos de revisión\n',
            f'{indent}        del st.session_state.pending_irl_responses\n',
            f'{indent}        \n',
            f'{indent}        st.success("✅ Respuestas aplicadas correctamente al sistema.")\n',
            f'{indent}        st.rerun()\n',
            '\n',
            f'{indent}with col_cancelar:\n',
            f'{indent}    if st.button("❌ Cancelar y subir otro archivo", use_container_width=True):\n',
            f'{indent}        # Limpiar todo sin aplicar\n',
            f'{indent}        if \'pending_irl_responses\' in st.session_state:\n',
            f'{indent}            del st.session_state.pending_irl_responses\n',
            f'{indent}        if \'irl_excel_file_loaded\' in st.session_state:\n',
            f'{indent}            del st.session_state.irl_excel_file_loaded\n',
            f'{indent}        if \'irl_revision_data\' in st.session_state:\n',
            f'{indent}            del st.session_state.irl_revision_data\n',
            f'{indent}        \n',
            f'{indent}        st.info("Archivo cancelado. Puedes subir un nuevo archivo.")\n',
            f'{indent}        st.rerun()\n',
            '    \n',
            lines[end_idx],  # Mantener la línea st.markdown("---")
        ]
        
        # Reemplazar las líneas
        lines[i:end_idx+1] = new_lines
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Archivo modificado exitosamente")
        break
else:
    print("❌ No se encontró la línea con col_aplicar")
