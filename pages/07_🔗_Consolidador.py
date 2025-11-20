"""
Página de Consolidación de Evaluaciones
========================================
Permite combinar archivos separados de Portafolio, IRL y EBCT 
en un archivo consolidado único para la página de Indicadores.
"""

import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Consolidador de Evaluaciones",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 Consolidador de Evaluaciones")
st.caption("Combina archivos separados de Portafolio, IRL y EBCT en un archivo consolidado único")

st.markdown("---")

# Estado de archivos cargados
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.info("""
    **📂 Fase 0: Portafolio**
    - Información básica de proyectos
    - ID, Nombre, Responsable, etc.
    - Archivo: `portafolio_actual_*.xlsx`
    """)

with col_info2:
    st.info("""
    **📈 Fase 1: IRL**
    - Evaluación de madurez tecnológica
    - 6 dimensiones × 9 niveles
    - Archivo: `evaluacion_IRL_*.xlsx`
    """)

with col_info3:
    st.info("""
    **🧭 Fase 2: EBCT**
    - 34 características organizacionales
    - Estados: Verde, Amarillo, Rojo
    - Archivo: `evaluacion_EBCT_*.xlsx`
    """)

st.markdown("---")

# Sección de carga de archivos
st.markdown("### 📤 Paso 1: Cargar archivos individuales")

col_upload1, col_upload2, col_upload3 = st.columns(3)

with col_upload1:
    st.markdown("#### 📂 Portafolio")
    portafolio_file = st.file_uploader(
        "Archivo de Portafolio",
        type=['xlsx', 'xls'],
        key='upload_portafolio_cons',
        help="Archivo descargado desde la Fase 0"
    )
    if portafolio_file:
        st.success(f"✅ {portafolio_file.name}")

with col_upload2:
    st.markdown("#### 📈 IRL")
    irl_file = st.file_uploader(
        "Archivo de IRL",
        type=['xlsx', 'xls'],
        key='upload_irl_cons',
        help="Archivo descargado desde la Fase 1"
    )
    if irl_file:
        st.success(f"✅ {irl_file.name}")

with col_upload3:
    st.markdown("#### 🧭 EBCT")
    ebct_file = st.file_uploader(
        "Archivo de EBCT",
        type=['xlsx', 'xls'],
        key='upload_ebct_cons',
        help="Archivo descargado desde la Fase 2"
    )
    if ebct_file:
        st.success(f"✅ {ebct_file.name}")

st.markdown("---")

# Validación y consolidación
if portafolio_file and irl_file and ebct_file:
    st.markdown("### 🔍 Paso 2: Validación de datos")
    
    try:
        # Leer archivos
        df_portafolio = pd.read_excel(portafolio_file)
        df_irl = pd.read_excel(irl_file)
        df_ebct = pd.read_excel(ebct_file)
        
        # Validaciones
        col_val1, col_val2, col_val3 = st.columns(3)
        
        with col_val1:
            proyectos_portafolio = set(df_portafolio['ID_Proyecto'].unique()) if 'ID_Proyecto' in df_portafolio.columns else set()
            st.metric("Proyectos en Portafolio", len(proyectos_portafolio))
        
        with col_val2:
            proyectos_irl = set(df_irl['ID_Proyecto'].unique()) if 'ID_Proyecto' in df_irl.columns else set()
            st.metric("Proyectos en IRL", len(proyectos_irl))
        
        with col_val3:
            proyectos_ebct = set(df_ebct['ID_Proyecto'].unique()) if 'ID_Proyecto' in df_ebct.columns else set()
            st.metric("Proyectos en EBCT", len(proyectos_ebct))
        
        # Validación cruzada
        st.markdown("#### ✅ Validación cruzada de IDs")
        
        inconsistencias = []
        
        if proyectos_irl - proyectos_portafolio:
            inconsistencias.append(f"⚠️ IRL tiene proyectos no registrados en Portafolio: {proyectos_irl - proyectos_portafolio}")
        
        if proyectos_ebct - proyectos_portafolio:
            inconsistencias.append(f"⚠️ EBCT tiene proyectos no registrados en Portafolio: {proyectos_ebct - proyectos_portafolio}")
        
        proyectos_comunes = proyectos_portafolio & proyectos_irl & proyectos_ebct
        
        if inconsistencias:
            for inc in inconsistencias:
                st.warning(inc)
            st.info(f"✅ Proyectos con datos completos: {len(proyectos_comunes)}")
        else:
            st.success(f"✅ Todos los IDs son consistentes. {len(proyectos_comunes)} proyectos completos.")
        
        st.markdown("---")
        
        # Generar consolidado
        st.markdown("### 📦 Paso 3: Generar archivo consolidado")
        
        col_gen1, col_gen2 = st.columns([2, 1])
        
        with col_gen1:
            st.info("""
            **El archivo consolidado contendrá:**
            - 📄 Hoja 'Indice': Información de portafolio
            - 📊 Hoja 'IRL': Evaluaciones de madurez tecnológica
            - 🎯 Hoja 'EBCT': Características organizacionales
            - 📅 Hoja 'Acciones': Plan de acción (si existe en EBCT)
            """)
        
        with col_gen2:
            if st.button("🚀 Generar Consolidado", type="primary", use_container_width=True):
                try:
                    # Crear archivo consolidado
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        # Hoja Indice (Portafolio)
                        df_portafolio.to_excel(writer, sheet_name='Indice', index=False)
                        
                        # Hoja IRL
                        df_irl.to_excel(writer, sheet_name='IRL', index=False)
                        
                        # Hoja EBCT
                        df_ebct.to_excel(writer, sheet_name='EBCT', index=False)
                        
                        # Hoja Acciones (si existe)
                        if 'Descripcion' in df_ebct.columns:  # Asumir que tiene plan de acción
                            # Extraer columnas de plan de acción
                            cols_accion = [col for col in df_ebct.columns if 'Accion' in col or 'Responsable' in col or 'Fecha' in col or 'Completado' in col]
                            if cols_accion:
                                df_acciones = df_ebct[['ID_Proyecto'] + cols_accion].dropna(subset=['ID_Proyecto'])
                                df_acciones.to_excel(writer, sheet_name='Acciones', index=False)
                    
                    # Botón de descarga
                    st.download_button(
                        label="⬇️ Descargar Archivo Consolidado",
                        data=buffer.getvalue(),
                        file_name=f"CONSOLIDADO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.success("✅ Archivo consolidado generado correctamente")
                    
                    st.markdown("""
                    ---
                    ### 📖 Próximos pasos:
                    1. Descarga el archivo consolidado
                    2. Ve a la página **📊 Indicadores y Seguimiento**
                    3. Carga el archivo consolidado
                    4. ¡Visualiza todos los indicadores y métricas!
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error al generar consolidado: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error al leer archivos: {str(e)}")
        st.info("Verifica que los archivos tengan el formato correcto y contengan las columnas esperadas.")

else:
    st.warning("⚠️ Carga los 3 archivos (Portafolio, IRL y EBCT) para continuar")
    
    st.markdown("---")
    
    # Ayuda
    with st.expander("❓ ¿Cómo obtener los archivos individuales?"):
        st.markdown("""
        ### 📂 Fase 0 - Portafolio:
        1. Ve a la página **Fase 0 - Portafolio**
        2. Carga tus proyectos (o usa los existentes)
        3. Haz clic en **"📤 Descargar datos actuales"**
        
        ### 📈 Fase 1 - IRL:
        1. Ve a la página **Fase 1 - IRL**
        2. Evalúa tus proyectos (o usa evaluaciones existentes)
        3. Descarga el archivo de evaluación
        
        ### 🧭 Fase 2 - EBCT:
        1. Ve a la página **Fase 2 - EBCT**
        2. Evalúa las 34 características
        3. Descarga el archivo de evaluación EBCT
        
        **💡 Tip**: Si ya tienes evaluaciones guardadas, puedes descargarlas directamente desde cada fase sin necesidad de re-evaluar.
        """)

st.markdown("---")

# Footer con instrucciones
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; color: white; text-align: center;'>
    <h3>🎯 Flujo de Trabajo Recomendado</h3>
    <p style='font-size: 1.1rem; margin-top: 1rem;'>
        <strong>Fase 0</strong> → Portafolio de proyectos<br>
        <strong>Fase 1</strong> → Evaluación IRL<br>
        <strong>Fase 2</strong> → Evaluación EBCT<br>
        <strong>Consolidador</strong> → Combinar todo<br>
        <strong>Indicadores</strong> → Visualizar y analizar
    </p>
</div>
""", unsafe_allow_html=True)
