# Script para reemplazar toda la sección de botones IRL

filepath = r'c:\Users\Grupo DeiDanilo\Desktop\JOSE PABLO\Gestor Base\pages\03_📈_Fase_1_IRL.py'

# Leer el archivo
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar la sección a reemplazar
old_text_start = "# Botones de acción para archivo revisado\n    if st.session_state.get('irl_excel_file_loaded') and 'pending_irl_responses' in st.session_state:"
old_text_end = "st.rerun()\n    \n    st.markdown(\"---\")\n    \n    # Paso 3: Botón Evaluar"

new_section = """# Botones de acción para archivo revisado
    if st.session_state.get('irl_excel_file_loaded') and 'pending_irl_responses' in st.session_state:
        st.markdown("---")
        st.markdown("##### ✅ Confirmar y Aplicar")
        
        col_aplicar, col_cancelar = st.columns([1, 1])
        
        with col_aplicar:
            if st.button("✅ Aplicar respuestas al sistema", use_container_width=True, type="primary"):
                # Aplicar todas las respuestas al session_state
                for key, value in st.session_state.pending_irl_responses.items():
                    st.session_state[key] = value
                
                # Marcar como aplicado
                st.session_state.irl_responses_applied = True
                
                # Limpiar pendientes pero mantener datos de revisión
                del st.session_state.pending_irl_responses
                
                st.success("✅ Respuestas aplicadas correctamente al sistema.")
                st.rerun()
        
        with col_cancelar:
            if st.button("❌ Cancelar y subir otro archivo", use_container_width=True):
                # Limpiar todo sin aplicar
                if 'pending_irl_responses' in st.session_state:
                    del st.session_state.pending_irl_responses
                if 'irl_excel_file_loaded' in st.session_state:
                    del st.session_state.irl_excel_file_loaded
                if 'irl_revision_data' in st.session_state:
                    del st.session_state.irl_revision_data
                
                st.info("Archivo cancelado. Puedes subir un nuevo archivo.")
                st.rerun()
    
    st.markdown("---")
    
    # Paso 3: Botón Evaluar"""

# Buscar el inicio
start_idx = content.find(old_text_start)
if start_idx == -1:
    print("NO se encontró el inicio de la sección")
else:
    # Buscar el final después del inicio
    end_idx = content.find(old_text_end, start_idx)
    if end_idx == -1:
        print("NO se encontró el final de la sección")
    else:
        # Reemplazar
        new_content = content[:start_idx] + new_section + content[end_idx + len(old_text_end) - 18:]  # Mantener "# Paso 3: Botón Evaluar"
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Sección reemplazada correctamente")
        print(f"   Inicio en: {start_idx}")
        print(f"   Final en: {end_idx}")
