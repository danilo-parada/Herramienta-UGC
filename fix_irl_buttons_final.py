# Script simple para reemplazar línea por línea

filepath = r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py'

# Leer todas las líneas
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar y reemplazar líneas específicas
modified = False
for i, line in enumerate(lines):
    # Buscar la línea con el botón corrupto (línea 3144)
    if 'Cargar respuestas al sistema' in line and 'st.button' in line:
        print(f"Línea {i+1} ANTES: {repr(line[:80])}")
        
        # Reemplazar desde aquí las siguientes líneas
        # Necesitamos reemplazar desde la línea del botón hasta st.rerun()
        
        # Encontrar el índice donde termina esta sección
        j = i
        while j < len(lines) and 'st.markdown("---")' not in lines[j]:
            j += 1
        
        # Crear el nuevo bloque
        indent = '        '  # 8 espacios de indentación
        new_block = [
            f'{indent}st.markdown("---")\n',
            f'{indent}st.markdown("##### ✅ Confirmar y Aplicar")\n',
            f'{indent}\n',
            f'{indent}col_aplicar, col_cancelar = st.columns([1, 1])\n',
            f'{indent}\n',
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
            f'{indent}\n',
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
        ]
        
        # Reemplazar desde línea i-2 (las líneas de caption) hasta j (exclusivo)
        start_replace = i - 2
        lines[start_replace:j] = new_block
        
        modified = True
        print(f"✅ Sección reemplazada desde línea {start_replace+1} hasta {j+1}")
        break

if modified:
    # Guardar el archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Archivo guardado correctamente")
else:
    print("❌ No se encontró la línea a reemplazar")
