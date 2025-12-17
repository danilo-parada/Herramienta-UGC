"""
Página 06: Fase 4 Indicadores
Sistema de gestión de indicadores de desempeño para múltiples proyectos de innovación
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from html import escape
import io
import numpy as np
import sys
from pathlib import Path

# Agregar path para importar módulos core
sys.path.append(str(Path(__file__).parent.parent))

from core.ebct import EBCT_CHARACTERISTICS
from core.theme import load_theme
from core.components import render_page_banner

# Configuración de la página
st.set_page_config(
    page_title="Fase 4 Indicadores",
    page_icon="📈",
    layout="wide"
)
load_theme()

render_page_banner(
    title="Fase 4 Indicadores",
    subtitle="Sistema de gestión y monitoreo de indicadores de desempeño de proyectos",
    body="Visualiza el rendimiento de tu portafolio de proyectos. Compara niveles IRL, cumplimiento EBCT y otros KPIs clave para la toma de decisiones estratégicas.",
    chips=[
        {"label": "GP", "title": "Gestión de Portafolio"},
        {"label": "MK", "title": "Monitoreo de KPIs"},
        {"label": "CP", "title": "Comparativa de Proyectos"},
    ]
)

# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

if 'proyectos_db' not in st.session_state:
    st.session_state.proyectos_db = None

if 'proyecto_actual_idx' not in st.session_state:
    st.session_state.proyecto_actual_idx = None

# Procesar eliminación de base si fue solicitado
if st.session_state.get('eliminar_base', False):
    # Limpiar completamente el session_state relacionado con proyectos
    keys_to_delete = []
    for key in st.session_state.keys():
        if 'proyecto' in key.lower() or 'indicador' in key.lower():
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Reinicializar
    st.session_state.proyectos_db = None
    st.session_state.proyecto_actual_idx = None
    st.session_state.eliminar_base = False
    
    # Limpiar cache
    st.cache_data.clear()
    
    st.success("✅ Base de ejemplo eliminada correctamente. Ahora puedes cargar nuevos datos.")
    st.stop()

# ============================================================================
# FUNCIÓN: GENERAR PLANTILLA EXCEL CON SIMULACIÓN DE 10 PROYECTOS
# ============================================================================

def generar_plantilla_proyectos() -> bytes:
    """Genera plantilla Excel con estructura para 10 proyectos de ejemplo"""
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # ===== HOJA 1: ÍNDICE DE PROYECTOS =====
        proyectos_ejemplo = []
        for i in range(1, 11):
            proyectos_ejemplo.append({
                'ID_Proyecto': f'PROY-{i:03d}',
                'Nombre_Proyecto': f'Proyecto de Innovación {i}',
                'Responsable': f'Investigador {i}',
                'Fecha_Inicio': '2025-01-01',
                'Fecha_Actualizacion': datetime.now().strftime('%Y-%m-%d'),
                'Estado': 'En Progreso' if i <= 7 else 'Completado',
                'Nivel_IRL_Promedio': np.random.randint(3, 9),
                'Caracteristicas_Criticas': np.random.randint(5, 20),
                'Avance_Diagnostico': np.random.randint(30, 100),
                'Presupuesto_Total': np.random.randint(10000, 100000),
                'Notas': ''
            })
        
        df_proyectos = pd.DataFrame(proyectos_ejemplo)
        df_proyectos.to_excel(writer, sheet_name='Índice_Proyectos', index=False)
        
        # Ajustar anchos
        ws_indice = writer.sheets['Índice_Proyectos']
        ws_indice.column_dimensions['A'].width = 15
        ws_indice.column_dimensions['B'].width = 35
        ws_indice.column_dimensions['C'].width = 25
        ws_indice.column_dimensions['D'].width = 15
        ws_indice.column_dimensions['E'].width = 20
        ws_indice.column_dimensions['F'].width = 15
        ws_indice.column_dimensions['G'].width = 20
        ws_indice.column_dimensions['H'].width = 25
        ws_indice.column_dimensions['I'].width = 20
        ws_indice.column_dimensions['J'].width = 20
        ws_indice.column_dimensions['K'].width = 40
        
        # ===== HOJA 2: PREGUNTAS IRL (151 PREGUNTAS REALES) =====
        # Importar las dimensiones y niveles IRL (simplificado para ejemplo)
        dimensiones_irl = [
            'Investigación y Validación Técnica',
            'Estrategia de Propiedad Intelectual',
            'Preparación del Mercado',
            'Preparación Organizacional',
            'Evaluación de Riesgos y Financiamiento',
            'Estrategia y Gestión para Exportación'
        ]
        
        irl_preguntas_data = []
        pregunta_id = 1
        
        # Generar 151 preguntas distribuidas en 6 dimensiones (aproximadamente 25 por dimensión)
        for i in range(1, 11):  # 10 proyectos
            for dim in dimensiones_irl:
                # Aproximadamente 25 preguntas por dimensión
                num_preguntas = 25 if dim != 'Estrategia y Gestión para Exportación' else 26
                for q in range(1, num_preguntas + 1):
                    nivel = ((q - 1) // 3) + 1  # 3 preguntas por nivel aproximadamente
                    if nivel > 9:
                        nivel = 9
                    
                    irl_preguntas_data.append({
                        'ID_Proyecto': f'PROY-{i:03d}',
                        'Dimension': dim,
                        'Nivel': nivel,
                        'ID_Pregunta': f'Q{pregunta_id:03d}',
                        'Pregunta': f'Pregunta {q} de nivel {nivel} para {dim}',
                        'Respuesta': np.random.choice(['VERDADERO', 'FALSO'], p=[0.6, 0.4]),
                        'Evidencia': '',
                        'Observaciones': ''
                    })
            pregunta_id += 1
        
        df_irl_preguntas = pd.DataFrame(irl_preguntas_data)
        df_irl_preguntas.to_excel(writer, sheet_name='Preguntas_IRL', index=False)
        
        # ===== HOJA 3: NIVELES IRL POR PROYECTO =====
        irl_data = []
        for i in range(1, 11):
            for dim in dimensiones_irl:
                irl_data.append({
                    'ID_Proyecto': f'PROY-{i:03d}',
                    'Dimension': dim,
                    'Nivel_Alcanzado': np.random.randint(1, 9),
                    'Nivel_Meta': 9,
                    'Porcentaje_Cumplimiento': np.random.randint(30, 100),
                    'Observaciones': ''
                })
        
        df_irl = pd.DataFrame(irl_data)
        df_irl.to_excel(writer, sheet_name='Niveles_IRL', index=False)
        
        # ===== HOJA 4: CARACTERÍSTICAS EBCT (34 CARACTERÍSTICAS REALES) =====
        ebct_data = []
        for i in range(1, 11):
            for char in EBCT_CHARACTERISTICS:
                # Usar números en lugar de emojis: 1=Rojo, 2=Amarillo, 3=Verde
                estado_num = np.random.choice([1, 2, 3], p=[0.2, 0.3, 0.5])
                
                ebct_data.append({
                    'ID_Proyecto': f'PROY-{i:03d}',
                    'ID_Caracteristica': char['id'],
                    'Fase': char['phase_name'],
                    'Caracteristica': char['name'],
                    'Estado_Color': estado_num,  # 1=Rojo, 2=Amarillo, 3=Verde
                    'Score': np.random.uniform(0, 1),
                    'Cumple': np.random.choice(['Sí', 'No'], p=[0.7, 0.3]),
                    'Observaciones': ''
                })
        
        df_ebct = pd.DataFrame(ebct_data)
        df_ebct.to_excel(writer, sheet_name='Características_EBCT', index=False)
        
        # ===== HOJA 5: PLAN DE ACCIÓN POR PROYECTO =====
        accion_data = []
        for i in range(1, 11):
            num_acciones = np.random.randint(3, 10)
            for j in range(1, num_acciones + 1):
                accion_data.append({
                    'ID_Proyecto': f'PROY-{i:03d}',
                    'ID_Accion': j,
                    'ID_Caracteristica': np.random.randint(1, 35),
                    'Descripcion': f'Acción de mejora {j}',
                    'Responsable': f'Responsable {np.random.randint(1, 5)}',
                    'Recursos': f'Recurso tipo {np.random.randint(1, 3)}',
                    'Presupuesto': np.random.randint(1000, 20000),
                    'Fecha_Inicio': '2025-01-15',
                    'Fecha_Fin': '2025-06-30',
                    'Avance_Porcentaje': np.random.randint(0, 100),
                    'Completado': np.random.choice(['Sí', 'No'], p=[0.4, 0.6]),
                    'Observaciones': ''
                })
        
        df_acciones = pd.DataFrame(accion_data)
        df_acciones.to_excel(writer, sheet_name='Plan_Acción', index=False)
        
        # ===== HOJA 6: INDICADORES DE DESEMPEÑO =====
        indicadores_data = []
        for i in range(1, 11):
            indicadores_data.append({
                'ID_Proyecto': f'PROY-{i:03d}',
                'Indicador_IRL_Promedio': np.random.randint(3, 9),
                'Indicador_Cumplimiento_EBCT': np.random.randint(40, 95),
                'Indicador_Avance_Acciones': np.random.randint(30, 100),
                'Indicador_Presupuesto_Ejecutado': np.random.randint(20, 90),
                'Indicador_Caracteristicas_Verde': np.random.randint(50, 90),
                'Indicador_Caracteristicas_Amarillo': np.random.randint(5, 30),
                'Indicador_Caracteristicas_Rojo': np.random.randint(0, 20),
                'Indicador_Madurez_Global': np.random.randint(50, 95),
                'Dias_Transcurridos': np.random.randint(30, 365),
                'Observaciones': ''
            })
        
        df_indicadores = pd.DataFrame(indicadores_data)
        df_indicadores.to_excel(writer, sheet_name='Indicadores_Desempeño', index=False)
        
        # ===== HOJA 7: INSTRUCTIVO =====
        instructivo = {
            'INSTRUCCIONES': [
                '=' * 80,
                'SISTEMA FASE 4: INDICADORES DE DESEMPEÑO DE PROYECTOS DE INNOVACIÓN',
                '=' * 80,
                '',
                '1. ÍNDICE DE PROYECTOS:',
                '   - Contiene la lista de todos los proyectos con información general',
                '   - ID_Proyecto: Código único de identificación',
                '   - Actualice campos según avance real del proyecto',
                '',
                '2. PREGUNTAS IRL (151 PREGUNTAS):',
                '   - Lista completa de 151 preguntas de evaluación IRL',
                '   - 6 dimensiones con aproximadamente 25 preguntas cada una',
                '   - Respuesta: VERDADERO o FALSO',
                '   - Evidencia y Observaciones opcionales',
                '',
                '3. NIVELES IRL:',
                '   - Resumen calculado por dimensión',
                '   - Nivel_Alcanzado: Nivel actual conseguido (1-9)',
                '   - Nivel_Meta: Nivel objetivo (normalmente 9)',
                '   - Porcentaje_Cumplimiento: Auto-calculable',
                '',
                '4. CARACTERÍSTICAS EBCT (34 CARACTERÍSTICAS REALES):',
                '   - Lista completa de las 34 características EBCT oficiales',
                '   - Estado_Color: Código numérico (1=Rojo, 2=Amarillo, 3=Verde)',
                '   - 1 = 🔴 Rojo (No cumple)',
                '   - 2 = 🟡 Amarillo (En desarrollo)',
                '   - 3 = 🟢 Verde (Sí cumple)',
                '   - Score: Valor de cumplimiento (0-1)',
                '',
                '5. PLAN DE ACCIÓN:',
                '   - Acciones específicas por proyecto',
                '   - Vincular con ID_Caracteristica correspondiente (1-34)',
                '   - Actualizar Avance_Porcentaje según progreso',
                '',
                '6. INDICADORES DE DESEMPEÑO:',
                '   - Métricas consolidadas por proyecto',
                '   - Indicadores calculados automáticamente al cargar',
                '',
                '=' * 80,
                'FLUJO DE TRABAJO:',
                '=' * 80,
                '1. Descargar esta plantilla',
                '2. Completar/actualizar información de proyectos',
                '3. En Preguntas_IRL: Responder VERDADERO o FALSO a las 151 preguntas',
                '4. En Características_EBCT: Asignar estado (1, 2 o 3) a las 34 características',
                '5. Cargar archivo en la aplicación',
                '6. Visualizar panel de indicadores',
                '7. Descargar versión actualizada con métricas',
                '',
                'NOTA: Mantenga la estructura de las hojas sin modificar nombres de columnas',
                '',
                'CÓDIGOS DE ESTADO EBCT:',
                '  1 = Rojo (No cumple) - Requiere acción inmediata',
                '  2 = Amarillo (En desarrollo) - En progreso',
                '  3 = Verde (Sí cumple) - Completado satisfactoriamente'
            ]
        }
        
        df_instructivo = pd.DataFrame(instructivo)
        df_instructivo.to_excel(writer, sheet_name='Instructivo', index=False, header=False)
    
    output.seek(0)
    return output.getvalue()

# ============================================================================
# FUNCIÓN: CARGAR DATOS DESDE EXCEL
# ============================================================================

def cargar_proyectos_desde_excel(file) -> dict:
    """Carga proyectos desde archivo Excel"""
    try:
        # Leer todas las hojas
        indice = pd.read_excel(file, sheet_name='Índice_Proyectos')
        irl = pd.read_excel(file, sheet_name='Niveles_IRL')
        ebct = pd.read_excel(file, sheet_name='Características_EBCT')
        acciones = pd.read_excel(file, sheet_name='Plan_Acción')
        indicadores = pd.read_excel(file, sheet_name='Indicadores_Desempeño')
        
        # Convertir códigos numéricos a etiquetas con emojis para visualización
        if 'Estado_Color' in ebct.columns:
            mapeo_estados = {
                1: '🔴 Rojo',
                2: '🟡 Amarillo',
                3: '🟢 Verde'
            }
            ebct['Estado_Display'] = ebct['Estado_Color'].map(mapeo_estados)
            # Usar Estado_Display como Estado_Actual para compatibilidad
            ebct['Estado_Actual'] = ebct['Estado_Display']
        
        # Intentar cargar hoja de preguntas IRL si existe
        preguntas_irl = None
        try:
            preguntas_irl = pd.read_excel(file, sheet_name='Preguntas_IRL')
        except:
            pass
        
        return {
            'indice': indice,
            'irl': irl,
            'ebct': ebct,
            'acciones': acciones,
            'indicadores': indicadores,
            'preguntas_irl': preguntas_irl,
            'timestamp': datetime.now()
        }
    except Exception as e:
        st.error(f"❌ Error al cargar archivo: {str(e)}")
        return None

# ============================================================================
# SECCIÓN 1: GESTIÓN DE ARCHIVOS
# ============================================================================

st.markdown("## 📁 Gestión de Base de Datos de Proyectos")

# Crear 3 columnas para las opciones
col_ejemplo, col_plantilla, col_upload = st.columns(3)

with col_ejemplo:
    st.markdown("### 🎯 Datos de Ejemplo")
    st.caption("Carga automática de 10 proyectos simulados para probar el sistema")
    
    # Verificar si los datos de ejemplo ya fueron cargados
    db = st.session_state.get('proyectos_db')
    ejemplo_ya_cargado_fase4 = isinstance(db, dict) and len(db.get('indice', [])) > 0
    
    if st.button("📊 Cargar Ejemplo", use_container_width=True, type="primary", key="btn_cargar_ejemplo", disabled=ejemplo_ya_cargado_fase4):
        with st.spinner("⏳ Generando datos de ejemplo..."):
            # Generar plantilla con datos de ejemplo
            plantilla_bytes = generar_plantilla_proyectos()
            
            # Cargar directamente en memoria
            datos = cargar_proyectos_desde_excel(io.BytesIO(plantilla_bytes))
            
            if datos:
                st.session_state.proyectos_db = datos
                
                # ===== RECALCULAR INDICADORES AUTOMÁTICAMENTE =====
                indicadores_recalculados = []
                
                for _, proyecto in datos['indice'].iterrows():
                    id_proy = proyecto['ID_Proyecto']
                    
                    # IRL promedio
                    irl_proy = datos['irl'][datos['irl']['ID_Proyecto'] == id_proy]
                    irl_promedio = irl_proy['Nivel_Alcanzado'].mean() if len(irl_proy) > 0 else 0
                    
                    # EBCT por colores
                    ebct_proy = datos['ebct'][datos['ebct']['ID_Proyecto'] == id_proy]
                    if 'Estado_Color' in ebct_proy.columns:
                        total_ebct = len(ebct_proy)
                        verdes = len(ebct_proy[ebct_proy['Estado_Color'] == 3])
                        amarillos = len(ebct_proy[ebct_proy['Estado_Color'] == 2])
                        rojos = len(ebct_proy[ebct_proy['Estado_Color'] == 1])
                        cumplimiento_ebct = (verdes / total_ebct * 100) if total_ebct > 0 else 0
                        pct_verde = (verdes / total_ebct * 100) if total_ebct > 0 else 0
                        pct_amarillo = (amarillos / total_ebct * 100) if total_ebct > 0 else 0
                        pct_rojo = (rojos / total_ebct * 100) if total_ebct > 0 else 0
                    else:
                        cumplimiento_ebct = 0
                        pct_verde = pct_amarillo = pct_rojo = 0
                    
                    # Avance de acciones
                    acciones_proy = datos['acciones'][datos['acciones']['ID_Proyecto'] == id_proy]
                    avance_acciones = acciones_proy['Avance_Porcentaje'].mean() if len(acciones_proy) > 0 else 0
                    
                    # Madurez global
                    madurez_global = (irl_promedio / 9 * 40 + cumplimiento_ebct * 0.6)
                    
                    indicadores_recalculados.append({
                        'ID_Proyecto': id_proy,
                        'Nombre_Proyecto': proyecto['Nombre_Proyecto'],
                        'Indicador_IRL_Promedio': irl_promedio,
                        'Indicador_Cumplimiento_EBCT': cumplimiento_ebct,
                        'Indicador_Caracteristicas_Verde': pct_verde,
                        'Indicador_Caracteristicas_Amarillo': pct_amarillo,
                        'Indicador_Caracteristicas_Rojo': pct_rojo,
                        'Indicador_Avance_Acciones': avance_acciones,
                        'Indicador_Madurez_Global': madurez_global
                    })
                
                # Guardar indicadores recalculados
                datos['indicadores_calculados'] = pd.DataFrame(indicadores_recalculados)
                st.session_state.proyectos_db = datos
                
                st.success("✅ Datos de ejemplo cargados correctamente")
                st.rerun()
    
    # Mostrar mensaje si el ejemplo ya fue cargado
    if ejemplo_ya_cargado_fase4:
        st.info("✅ Datos de ejemplo cargados - El botón está desactivado. Usa 'Cargar Datos Reales' o 'Limpiar Base' si deseas cambiar.", icon="ℹ️")

with col_plantilla:
    st.markdown("### 📥 Plantilla Vacía")
    st.caption("Descarga plantilla para completar con tus datos reales")
    
    if st.button("🔽 Generar Plantilla", use_container_width=True, type="secondary", key="btn_descargar_plantilla"):
        plantilla_bytes = generar_plantilla_proyectos()
        st.download_button(
            label="📄 Descargar Excel",
            data=plantilla_bytes,
            file_name=f"plantilla_proyectos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_plantilla"
        )
        st.info("💡 Descarga el archivo, compléta con tus datos y cárgalo abajo")

with col_upload:
    st.markdown("### 📤 Cargar Datos Reales")
    st.caption("Sube tu archivo Excel completado")
    
    uploaded_file = st.file_uploader(
        "Selecciona archivo",
        type=['xlsx'],
        help="Archivo Excel con estructura de plantilla",
        key="uploader_datos"
    )
    
    if uploaded_file:
        datos = cargar_proyectos_desde_excel(uploaded_file)
        if datos:
            st.session_state.proyectos_db = datos
            
            # ===== RECALCULAR INDICADORES AUTOMÁTICAMENTE =====
            with st.spinner("🔄 Recalculando indicadores..."):
                # Recalcular indicadores por proyecto
                indicadores_recalculados = []
                
                for _, proyecto in datos['indice'].iterrows():
                    id_proy = proyecto['ID_Proyecto']
                    
                    # IRL promedio
                    irl_proy = datos['irl'][datos['irl']['ID_Proyecto'] == id_proy]
                    irl_promedio = irl_proy['Nivel_Alcanzado'].mean() if len(irl_proy) > 0 else 0
                    
                    # EBCT por colores
                    ebct_proy = datos['ebct'][datos['ebct']['ID_Proyecto'] == id_proy]
                    if 'Estado_Color' in ebct_proy.columns:
                        total_ebct = len(ebct_proy)
                        verdes = len(ebct_proy[ebct_proy['Estado_Color'] == 3])
                        amarillos = len(ebct_proy[ebct_proy['Estado_Color'] == 2])
                        rojos = len(ebct_proy[ebct_proy['Estado_Color'] == 1])
                        cumplimiento_ebct = (verdes / total_ebct * 100) if total_ebct > 0 else 0
                        pct_verde = (verdes / total_ebct * 100) if total_ebct > 0 else 0
                        pct_amarillo = (amarillos / total_ebct * 100) if total_ebct > 0 else 0
                        pct_rojo = (rojos / total_ebct * 100) if total_ebct > 0 else 0
                    else:
                        cumplimiento_ebct = 0
                        pct_verde = pct_amarillo = pct_rojo = 0
                    
                    # Avance de acciones
                    acciones_proy = datos['acciones'][datos['acciones']['ID_Proyecto'] == id_proy]
                    avance_acciones = acciones_proy['Avance_Porcentaje'].mean() if len(acciones_proy) > 0 else 0
                    
                    # Madurez global
                    madurez_global = (irl_promedio / 9 * 40 + cumplimiento_ebct * 0.6)
                    
                    indicadores_recalculados.append({
                        'ID_Proyecto': id_proy,
                        'Nombre_Proyecto': proyecto['Nombre_Proyecto'],
                        'Indicador_IRL_Promedio': round(irl_promedio, 2),
                        'Indicador_Cumplimiento_EBCT': round(cumplimiento_ebct, 1),
                        'Indicador_Avance_Acciones': round(avance_acciones, 1),
                        'Indicador_Caracteristicas_Verde': round(pct_verde, 1),
                        'Indicador_Caracteristicas_Amarillo': round(pct_amarillo, 1),
                        'Indicador_Caracteristicas_Rojo': round(pct_rojo, 1),
                        'Indicador_Madurez_Global': round(madurez_global, 1),
                        'Total_Caracteristicas': len(ebct_proy),
                        'Total_Acciones': len(acciones_proy)
                    })
                
                # Actualizar indicadores en sesión
                datos['indicadores_calculados'] = pd.DataFrame(indicadores_recalculados)
                st.session_state.proyectos_db = datos
            
            st.success(f"✅ Base de datos cargada: {len(datos['indice'])} proyectos")
            st.success(f"🔄 Indicadores recalculados automáticamente")
            st.info(f"📅 Última actualización: {datos['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# ============================================================================
# BOTÓN PARA ELIMINAR BASE DE EJEMPLO
# ============================================================================

if st.session_state.proyectos_db:
    col_info, col_btn = st.columns([3, 1])
    
    with col_info:
        st.info("📊 **Base de datos cargada** - Los indicadores se muestran abajo. Si deseas cargar datos originales, elimina esta base primero.")
    
    with col_btn:
        if st.button("🗑️ Eliminar Base de Ejemplo", type="secondary", use_container_width=True, key="btn_eliminar_base"):
            st.session_state.eliminar_base = True
            st.rerun()

st.markdown("---")

# ============================================================================
# SECCIÓN 2: PANEL DE INDICADORES GENERALES
# ============================================================================

if st.session_state.proyectos_db:
    datos = st.session_state.proyectos_db
    df_indice = datos['indice']
    df_irl = datos['irl']
    df_ebct = datos['ebct']
    df_acciones = datos['acciones']
    
    # Usar indicadores recalculados si existen
    if 'indicadores_calculados' in datos:
        df_indicadores = datos['indicadores_calculados']
    else:
        df_indicadores = datos['indicadores']
    
    # ============================================================================
    # TABS: GENERALES vs COMPARATIVOS vs INDIVIDUALES
    # ============================================================================
    
    tab_general, tab_comparativo, tab_individual = st.tabs([
        "📊 Indicadores Generales",
        "⚖️ Análisis Comparativo",
        "🔍 Vista Individual"
    ])
    
    # ============================================================================
    # TAB 1: INDICADORES GENERALES
    # ============================================================================
    with tab_general:
        st.markdown("## 📊 Resumen Global de Portafolio")
        
        # Métricas globales
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("📁 Total Proyectos", len(df_indice))
        with col_m2:
            proyectos_activos = len(df_indice[df_indice['Estado'] == 'En Progreso'])
            st.metric("🟢 Proyectos Activos", proyectos_activos)
        with col_m3:
            cumplimiento_ebct = df_indicadores['Indicador_Cumplimiento_EBCT'].mean()
            st.metric("✅ Cumplimiento EBCT", f"{cumplimiento_ebct:.0f}%")
        with col_m4:
            presupuesto_total = df_indice['Presupuesto_Total'].sum()
            st.metric("💰 Presupuesto Total", f"${presupuesto_total:,.0f}")
        
        st.markdown("---")
        
        # ===== GRÁFICO: NIVELES IRL POR DIMENSIÓN =====
        st.markdown("### 📊 Niveles IRL por Dimensión y Proyecto")
        st.caption("🔵 Escala: 1 (mínimo) a 9 (máximo logro) | Las 6 dimensiones IRL se evalúan independientemente")
        
        # Preparar datos agrupados por dimensión
        irl_por_dimension = df_irl.groupby(['Dimension', 'ID_Proyecto'])['Nivel_Alcanzado'].first().reset_index()
        irl_con_nombres = irl_por_dimension.merge(
            df_indice[['ID_Proyecto', 'Nombre_Proyecto']], 
            on='ID_Proyecto'
        )
        
        # Agregar información de cumplimiento para tooltips
        irl_con_nombres = irl_con_nombres.merge(
            df_indicadores[['ID_Proyecto', 'Indicador_Cumplimiento_EBCT', 'Indicador_Madurez_Global']],
            on='ID_Proyecto',
            how='left'
        )
        
        # Crear texto personalizado para tooltips
        irl_con_nombres['Tooltip_Info'] = irl_con_nombres.apply(
            lambda row: (
                f"<b>{row['Nombre_Proyecto']}</b><br>"
                f"<b>Dimensión:</b> {row['Dimension']}<br>"
                f"<b>Nivel Alcanzado:</b> {row['Nivel_Alcanzado']}/9<br>"
                f"<b>Progreso:</b> {(row['Nivel_Alcanzado']/9*100):.1f}%<br>"
                f"<b>Cumplimiento EBCT:</b> {row['Indicador_Cumplimiento_EBCT']:.0f}%<br>"
                f"<b>Madurez Global:</b> {row['Indicador_Madurez_Global']:.1f}%<br>"
                f"<b>Estado:</b> {'⭐ Máximo' if row['Nivel_Alcanzado'] == 9 else '🔄 En progreso'}"
            ),
            axis=1
        )
        
        # Paleta de colores profesional para dimensiones (6 colores distintos)
        color_dimension_map = {
            'Investigación y Validación Técnica': '#1E88E5',  # Azul
            'Estrategia de Propiedad Intelectual': '#43A047',  # Verde
            'Preparación del Mercado': '#FB8C00',  # Naranja
            'Preparación Organizacional': '#8E24AA',  # Púrpura
            'Evaluación de Riesgos y Financiamiento': '#E53935',  # Rojo
            'Estrategia y Gestión para Exportación': '#00ACC1'  # Cyan
        }
        
        # Asignar colores
        irl_con_nombres['Color'] = irl_con_nombres['Dimension'].map(color_dimension_map)
        
        # Crear gráfico de barras con diseño profesional
        fig_irl_dimensiones = go.Figure()
        
        # Agrupar por proyecto para crear barras agrupadas
        for proyecto_id in irl_con_nombres['ID_Proyecto'].unique():
            datos_proyecto = irl_con_nombres[irl_con_nombres['ID_Proyecto'] == proyecto_id]
            nombre_proyecto = datos_proyecto['Nombre_Proyecto'].iloc[0]
            
            fig_irl_dimensiones.add_trace(go.Bar(
                name=nombre_proyecto,
                x=datos_proyecto['Dimension'],
                y=datos_proyecto['Nivel_Alcanzado'],
                marker=dict(
                    color=datos_proyecto['Color'],
                    line=dict(color='white', width=2),
                    pattern_shape="",  # Sin patrón por defecto
                ),
                text=datos_proyecto['Nivel_Alcanzado'],
                textposition='outside',
                textfont=dict(size=11, color='#333', family='Arial Black'),
                hovertemplate='%{customdata}<extra></extra>',
                customdata=datos_proyecto['Tooltip_Info'],
                showlegend=True,
                legendgroup=proyecto_id
            ))
        
        # Configuración del layout profesional
        fig_irl_dimensiones.update_layout(
            barmode='group',
            xaxis=dict(
                title=None,  # Sin título en eje X
                showticklabels=False,  # Ocultar etiquetas del eje X
                showgrid=False,
                linecolor='#e0e0e0',
                linewidth=2
            ),
            yaxis=dict(
                title=dict(
                    text="<b>Nivel Alcanzado (1-9)</b>",
                    font=dict(size=14, family='Arial', color='#1a237e')
                ),
                range=[0, 10],
                dtick=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='#e8eaf6',
                linecolor='#e0e0e0',
                linewidth=2,
                tickfont=dict(size=11)
            ),
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            height=550,
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial",
                bordercolor="#1E88E5"
            ),
            showlegend=False,  # Ocultar leyenda de proyectos
            margin=dict(l=80, r=40, t=40, b=80),  # Reducir margen inferior
            font=dict(family='Arial, sans-serif')
        )
        
        # Agregar línea de referencia para nivel máximo
        fig_irl_dimensiones.add_hline(
            y=9, 
            line_dash="dash", 
            line_color="#1565C0", 
            line_width=2,
            annotation_text="Nivel Máximo (9)",
            annotation_position="right",
            annotation_font_size=10,
            annotation_font_color="#1565C0"
        )
        
        # Agregar sombreado para zonas de madurez
        fig_irl_dimensiones.add_hrect(
            y0=7, y1=9, 
            fillcolor="#C8E6C9", 
            opacity=0.15, 
            layer="below", 
            line_width=0,
            annotation_text="Alto",
            annotation_position="left",
            annotation_font_size=9,
            annotation_font_color="#2E7D32"
        )
        fig_irl_dimensiones.add_hrect(
            y0=4, y1=7, 
            fillcolor="#FFF9C4", 
            opacity=0.15, 
            layer="below", 
            line_width=0,
            annotation_text="Medio",
            annotation_position="left",
            annotation_font_size=9,
            annotation_font_color="#F57C00"
        )
        fig_irl_dimensiones.add_hrect(
            y0=0, y1=4, 
            fillcolor="#FFCDD2", 
            opacity=0.15, 
            layer="below", 
            line_width=0,
            annotation_text="Bajo",
            annotation_position="left",
            annotation_font_size=9,
            annotation_font_color="#C62828"
        )
        
        st.plotly_chart(fig_irl_dimensiones, use_container_width=True, key="chart_irl_dimensiones_pro")
        
        # Leyenda de colores por dimensión
        st.markdown("#### 🎨 Código de Colores por Dimensión")
        cols_legend = st.columns(6)
        dimensiones_legend = [
            ("🔵 Investigación y Validación Técnica", "#1E88E5"),
            ("🟢 Propiedad Intelectual", "#43A047"),
            ("🟠 Preparación del Mercado", "#FB8C00"),
            ("🟣 Preparación Organizacional", "#8E24AA"),
            ("🔴 Riesgos y Financiamiento", "#E53935"),
            ("🔷 Exportación", "#00ACC1")
        ]
        
        for col, (dim_name, dim_color) in zip(cols_legend, dimensiones_legend):
            with col:
                st.markdown(
                    f'<div style="background-color:{dim_color}; padding:8px; border-radius:5px; text-align:center; color:white; font-size:10px; font-weight:bold;">'
                    f'{dim_name}</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        # ===== GRÁFICOS EN COLUMNAS =====
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### 🎯 Cumplimiento EBCT por Proyecto")
            st.caption("Porcentaje de características en estado 🟢 Verde")
            fig_ebct_cumpl = px.bar(
                df_indicadores.sort_values('Indicador_Cumplimiento_EBCT', ascending=False),
                x='Nombre_Proyecto',
                y='Indicador_Cumplimiento_EBCT',
                color='Indicador_Cumplimiento_EBCT',
                color_continuous_scale='Teal',
                labels={'Indicador_Cumplimiento_EBCT': 'Cumplimiento %', 'Nombre_Proyecto': 'Proyecto'}
            )
            fig_ebct_cumpl.update_layout(height=400, showlegend=False)
            fig_ebct_cumpl.update_xaxes(tickangle=-45)
            fig_ebct_cumpl.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_ebct_cumpl, use_container_width=True, key="chart_ebct_cumpl")
        
        with col_chart2:
            st.markdown("#### 🏆 Índice de Madurez Global")
            st.caption("📐 Fórmula: (IRL_promedio/9 × 40%) + (EBCT_cumplimiento × 60%)")
            fig_madurez = px.bar(
                df_indicadores.sort_values('Indicador_Madurez_Global', ascending=False),
                x='Nombre_Proyecto',
                y='Indicador_Madurez_Global',
                color='Indicador_Madurez_Global',
                color_continuous_scale='Blues',
                labels={'Indicador_Madurez_Global': 'Madurez %', 'Nombre_Proyecto': 'Proyecto'}
            )
            fig_madurez.update_layout(height=400, showlegend=False)
            fig_madurez.update_xaxes(tickangle=-45)
            fig_madurez.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_madurez, use_container_width=True, key="chart_madurez")
        
        st.markdown("---")
        
        # ===== TABLA RESUMEN =====
        st.markdown("### 📋 Resumen de Proyectos")
        
        # Información sobre cálculo de madurez
        with st.expander("ℹ️ Interpretación de Indicadores"):
            st.markdown("""
            **📊 Niveles IRL (Innovation Readiness Level)**
            - Se evalúan **6 dimensiones independientes** por proyecto
            - Escala: **1** (nivel mínimo) a **9** (máximo logro alcanzado)
            - No se calcula un "promedio" general, cada dimensión refleja madurez específica
            
            **✅ Cumplimiento EBCT**
            - Porcentaje de características en estado 🟢 Verde (completadas satisfactoriamente)
            - 34 características totales distribuidas en 4 fases
            
            **🏆 Índice de Madurez Global**
            - Métrica combinada que integra ambas evaluaciones
            - **Fórmula**: `(IRL_promedio / 9 × 40%) + (EBCT_cumplimiento × 60%)`
            - Componentes:
              - **40%** peso para madurez tecnológica (IRL)
              - **60%** peso para capacidades organizacionales (EBCT)
            - Resultado en escala 0-100%
            
            **🚦 Estados EBCT**
            - 🔴 **Rojo**: No cumple - Requiere acción inmediata
            - 🟡 **Amarillo**: En desarrollo - Progreso en curso
            - 🟢 **Verde**: Cumple - Completado satisfactoriamente
            """)
        
        # Preparar tabla con indicadores
        tabla_resumen = df_indice.merge(df_indicadores, on='ID_Proyecto', suffixes=('', '_ind'))
        
        # Calcular mínimo y máximo IRL por proyecto para mostrar rango
        irl_stats = df_irl.groupby('ID_Proyecto')['Nivel_Alcanzado'].agg(['min', 'max', 'mean']).reset_index()
        irl_stats.columns = ['ID_Proyecto', 'IRL_Min', 'IRL_Max', 'IRL_Promedio']
        
        tabla_resumen = tabla_resumen.merge(irl_stats, on='ID_Proyecto')
        
        # Crear columna con rango IRL
        tabla_resumen['IRL_Rango'] = tabla_resumen.apply(
            lambda row: f"{row['IRL_Min']:.0f}-{row['IRL_Max']:.0f}" if row['IRL_Min'] != row['IRL_Max'] else f"{row['IRL_Min']:.0f}",
            axis=1
        )
        
        # Usar Nombre_Proyecto del df_indice (sin sufijo)
        tabla_resumen = tabla_resumen[[
            'ID_Proyecto', 'Nombre_Proyecto', 'Responsable', 'Estado',
            'IRL_Rango', 'IRL_Promedio', 'Indicador_Cumplimiento_EBCT',
            'Indicador_Madurez_Global', 'Presupuesto_Total'
        ]].copy()
        
        # Renombrar columnas para mejor visualización
        tabla_resumen.columns = [
            'ID', 'Proyecto', 'Responsable', 'Estado',
            'IRL Rango', 'IRL Media', 'EBCT %', 'Madurez %', 'Presupuesto'
        ]
        
        st.dataframe(
            tabla_resumen.style.background_gradient(
                subset=['IRL Media', 'EBCT %', 'Madurez %'],
                cmap='YlGnBu',
                vmin=0,
                vmax=100
            ).format({
                'IRL Media': '{:.1f}/9',
                'EBCT %': '{:.0f}%',
                'Madurez %': '{:.0f}%',
                'Presupuesto': '${:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.caption("💡 **IRL Rango**: Muestra el nivel mínimo y máximo alcanzado entre las 6 dimensiones | **IRL Media**: Valor promedio de referencia")
    
    # ============================================================================
    # TAB 2: ANÁLISIS COMPARATIVO
    # ============================================================================
    with tab_comparativo:
        st.markdown("## ⚖️ Comparación entre Proyectos")
        
        # Selector múltiple de proyectos
        proyectos_disponibles = df_indice['ID_Proyecto'].tolist()
        proyectos_nombres = df_indice.set_index('ID_Proyecto')['Nombre_Proyecto'].to_dict()
        
        proyectos_seleccionados = st.multiselect(
            "Selecciona proyectos para comparar",
            options=proyectos_disponibles,
            default=proyectos_disponibles[:3] if len(proyectos_disponibles) >= 3 else proyectos_disponibles,
            format_func=lambda x: f"{x} - {proyectos_nombres[x]}"
        )
        
        if len(proyectos_seleccionados) >= 2:
            
            # ===== GRÁFICOS CIRCULARES: DISTRIBUCIÓN EBCT POR PROYECTO =====
            st.markdown("### � Distribución de Estados EBCT por Proyecto")
            st.caption("Gráficos circulares mostrando la proporción de características en cada estado")
            
            # Preparar datos para comparación
            ebct_comparacion = df_ebct[df_ebct['ID_Proyecto'].isin(proyectos_seleccionados)].copy()
            
            if 'Estado_Color' in ebct_comparacion.columns:
                # Crear columnas según cantidad de proyectos (máximo 4 por fila)
                num_proyectos = len(proyectos_seleccionados)
                cols_per_row = min(4, num_proyectos)
                
                # Calcular filas necesarias
                num_rows = (num_proyectos + cols_per_row - 1) // cols_per_row
                
                for row_idx in range(num_rows):
                    cols = st.columns(cols_per_row)
                    start_idx = row_idx * cols_per_row
                    end_idx = min(start_idx + cols_per_row, num_proyectos)
                    
                    for col_idx, proy in enumerate(proyectos_seleccionados[start_idx:end_idx]):
                        with cols[col_idx]:
                            ebct_proy = ebct_comparacion[ebct_comparacion['ID_Proyecto'] == proy]
                            
                            verdes = len(ebct_proy[ebct_proy['Estado_Color'] == 3])
                            amarillos = len(ebct_proy[ebct_proy['Estado_Color'] == 2])
                            rojos = len(ebct_proy[ebct_proy['Estado_Color'] == 1])
                            total = len(ebct_proy)
                            
                            # Crear gráfico de pie profesional
                            fig_pie = go.Figure(data=[go.Pie(
                                labels=['🟢 Verde', '🟡 Amarillo', '🔴 Rojo'],
                                values=[verdes, amarillos, rojos],
                                marker=dict(
                                    colors=['#2e7d32', '#f57c00', '#c62828'],
                                    line=dict(color='white', width=3)
                                ),
                                textinfo='label+percent',
                                textposition='inside',
                                textfont=dict(size=11, color='white', family='Arial Black'),
                                hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>',
                                hole=0.4,  # Donut chart
                                pull=[0.05 if verdes == max(verdes, amarillos, rojos) else 0,
                                      0.05 if amarillos == max(verdes, amarillos, rojos) else 0,
                                      0.05 if rojos == max(verdes, amarillos, rojos) else 0]
                            )])
                            
                            fig_pie.update_layout(
                                title=dict(
                                    text=f"<b>{proyectos_nombres[proy]}</b><br><sub>{total} características</sub>",
                                    font=dict(size=13, family='Arial'),
                                    x=0.5,
                                    xanchor='center'
                                ),
                                showlegend=False,
                                height=280,
                                margin=dict(t=60, b=20, l=20, r=20),
                                paper_bgcolor='rgba(0,0,0,0)',
                                annotations=[dict(
                                    text=f'<b>{verdes}</b><br>Verde',
                                    x=0.5, y=0.5,
                                    font=dict(size=14, color='#2e7d32'),
                                    showarrow=False
                                )]
                            )
                            
                            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_comp_{proy}")
            
            st.markdown("---")
            
            # ===== GRÁFICOS RADAR: COMPARACIÓN IRL Y EBCT =====
            st.markdown("### 🎯 Análisis Multidimensional")
            
            col_radar_irl, col_radar_ebct = st.columns(2)
            
            with col_radar_irl:
                st.markdown("#### 📡 Radar IRL - 6 Dimensiones")
                st.caption("Comparación de niveles alcanzados por dimensión IRL")
                
                # Preparar datos IRL para radar
                irl_comparacion = df_irl[df_irl['ID_Proyecto'].isin(proyectos_seleccionados)].copy()
                
                fig_radar_irl = go.Figure()
                
                # Paleta de colores para proyectos
                colores_proyectos = ['#1E88E5', '#43A047', '#FB8C00', '#8E24AA', '#E53935', '#00ACC1', 
                                     '#FDD835', '#F06292', '#7CB342', '#5E35B1']
                
                for idx, proy in enumerate(proyectos_seleccionados):
                    irl_proy = irl_comparacion[irl_comparacion['ID_Proyecto'] == proy].sort_values('Dimension')
                    
                    fig_radar_irl.add_trace(go.Scatterpolar(
                        r=irl_proy['Nivel_Alcanzado'].tolist(),
                        theta=irl_proy['Dimension'].tolist(),
                        fill='toself',
                        name=proyectos_nombres[proy],
                        line=dict(color=colores_proyectos[idx % len(colores_proyectos)], width=3),
                        fillcolor=f"rgba{tuple(list(int(colores_proyectos[idx % len(colores_proyectos)][i:i+2], 16) for i in (1, 3, 5)) + [0.15])}",
                        hovertemplate='<b>%{theta}</b><br>Nivel: %{r}/9<extra></extra>'
                    ))
                
                fig_radar_irl.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 9],
                            tickmode='linear',
                            tick0=0,
                            dtick=1,
                            gridcolor='#e0e0e0',
                            gridwidth=1
                        ),
                        angularaxis=dict(
                            gridcolor='#e0e0e0',
                            linecolor='#bdbdbd'
                        ),
                        bgcolor='#fafafa'
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=-0.3,
                        xanchor='center',
                        x=0.5,
                        font=dict(size=10)
                    ),
                    height=500,
                    margin=dict(t=40, b=100, l=40, r=40),
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig_radar_irl, use_container_width=True, key="radar_irl_comp")
            
            with col_radar_ebct:
                st.markdown("#### 🎯 Radar EBCT - 4 Fases")
                st.caption("Comparación de cumplimiento por fase EBCT")
                
                # Preparar datos EBCT para radar por fases
                ebct_comp_radar = ebct_comparacion.copy()
                
                # Normalizar nombres de fase
                mapeo_fases_radar = {
                    "Fase 1": "Fase Incipiente",
                    "Fase 2": "Fase Validación y PI",
                    "Fase 3": "Fase Preparación para Mercado",
                    "Fase 4": "Fase Internacionalización"
                }
                
                if 'Fase' in ebct_comp_radar.columns:
                    ebct_comp_radar['Fase_Normalizada'] = ebct_comp_radar['Fase'].map(mapeo_fases_radar).fillna(ebct_comp_radar['Fase'])
                
                fig_radar_ebct = go.Figure()
                
                fases_orden = [
                    "Fase Incipiente",
                    "Fase Validación y PI",
                    "Fase Preparación para Mercado",
                    "Fase Internacionalización"
                ]
                
                for idx, proy in enumerate(proyectos_seleccionados):
                    ebct_proy = ebct_comp_radar[ebct_comp_radar['ID_Proyecto'] == proy]
                    
                    # Calcular % cumplimiento por fase (verdes/total * 100)
                    cumplimiento_por_fase = []
                    for fase in fases_orden:
                        fase_data = ebct_proy[ebct_proy.get('Fase_Normalizada', ebct_proy.get('Fase', '')) == fase]
                        if len(fase_data) > 0:
                            verdes_fase = len(fase_data[fase_data['Estado_Color'] == 3])
                            cumplimiento = (verdes_fase / len(fase_data)) * 100
                        else:
                            cumplimiento = 0
                        cumplimiento_por_fase.append(cumplimiento)
                    
                    fig_radar_ebct.add_trace(go.Scatterpolar(
                        r=cumplimiento_por_fase,
                        theta=[f.replace('Fase ', 'F') for f in fases_orden],
                        fill='toself',
                        name=proyectos_nombres[proy],
                        line=dict(color=colores_proyectos[idx % len(colores_proyectos)], width=3),
                        fillcolor=f"rgba{tuple(list(int(colores_proyectos[idx % len(colores_proyectos)][i:i+2], 16) for i in (1, 3, 5)) + [0.15])}",
                        hovertemplate='<b>%{theta}</b><br>Cumplimiento: %{r:.1f}%<extra></extra>'
                    ))
                
                fig_radar_ebct.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            tickmode='linear',
                            tick0=0,
                            dtick=20,
                            ticksuffix='%',
                            gridcolor='#e0e0e0',
                            gridwidth=1
                        ),
                        angularaxis=dict(
                            gridcolor='#e0e0e0',
                            linecolor='#bdbdbd'
                        ),
                        bgcolor='#fafafa'
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=-0.3,
                        xanchor='center',
                        x=0.5,
                        font=dict(size=10)
                    ),
                    height=500,
                    margin=dict(t=40, b=100, l=40, r=40),
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig_radar_ebct, use_container_width=True, key="radar_ebct_comp")
            
            st.markdown("---")
            
            # ===== MATRIZ DE SEMÁFOROS EBCT =====
            st.markdown("### 🚦 Matriz de Semáforos EBCT - Comparación por Proyecto")
            st.caption("Vista horizontal tipo matriz. Cada proyecto muestra sus características EBCT organizadas por fase con ID y color según estado.")
            
            # Filtrar solo proyectos seleccionados
            ebct_comparacion_full = df_ebct[df_ebct['ID_Proyecto'].isin(proyectos_seleccionados)].copy()
            
            # Definir las 4 fases EBCT
            fases_ebct = [
                "Fase Incipiente",
                "Fase Validación y PI",
                "Fase Preparación para Mercado",
                "Fase Internacionalización"
            ]
            
            # Mapeo de nombres de fase (si están diferentes en los datos)
            mapeo_fases = {
                "Fase 1": "Fase Incipiente",
                "Fase 2": "Fase Validación y PI",
                "Fase 3": "Fase Preparación para Mercado",
                "Fase 4": "Fase Internacionalización"
            }
            
            # Normalizar nombres de fase
            if 'Fase' in ebct_comparacion_full.columns:
                ebct_comparacion_full['Fase_Normalizada'] = ebct_comparacion_full['Fase'].map(mapeo_fases).fillna(ebct_comparacion_full['Fase'])
            
            # Colores por fase
            fase_colors = {
                "Fase Incipiente": "#673AB7",
                "Fase Validación y PI": "#4CAF50",
                "Fase Preparación para Mercado": "#2196F3",
                "Fase Internacionalización": "#FFC107"
            }
            
            # CSS para matriz de semáforo (mismo estilo de Fase 2)
            semaforo_css = """
<style>
.semaforo-matriz-proyectos {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin: 2rem 0;
    width: 100%;
}

.proyecto-box {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border: 3px solid #e0e0e0;
    transition: all 0.3s ease;
}

.proyecto-box:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    transform: translateY(-2px);
}

.proyecto-titulo {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-align: center;
    padding: 0.8rem;
    border-radius: 8px;
    background: linear-gradient(135deg, #1565C0, #1E88E5);
    color: white;
}

.fases-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
}

.fase-columna {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 0.6rem;
    border-top: 4px solid;
}

.fase-nombre {
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    text-align: center;
    color: white;
    padding: 0.4rem;
    border-radius: 5px;
}

.ids-container-fase {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    min-height: 60px;
    justify-content: center;
}

.id-box-semaforo {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.85rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.id-box-semaforo:hover {
    transform: scale(1.3);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    z-index: 100;
}

.id-box-semaforo.verde {
    background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
}

.id-box-semaforo.amarillo {
    background: linear-gradient(135deg, #f9a825 0%, #fdd835 100%);
    color: #333;
}

.id-box-semaforo.rojo {
    background: linear-gradient(135deg, #c62828 0%, #ef5350 100%);
}

.tooltip-semaforo {
    display: none;
    position: absolute;
    bottom: 110%;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, rgba(0,0,0,0.95), rgba(27,94,32,0.95));
    color: white;
    padding: 12px 14px;
    border-radius: 8px;
    border: 2px solid #2e7d32;
    box-shadow: 0 6px 20px rgba(0,0,0,0.7);
    white-space: nowrap;
    z-index: 1000;
    font-size: 0.75rem;
    line-height: 1.5;
    text-align: left;
    min-width: 200px;
    pointer-events: none;
}

.id-box-semaforo:hover .tooltip-semaforo {
    display: block;
}

.empty-fase-semaforo {
    text-align: center;
    color: #999;
    font-size: 0.7rem;
    padding: 0.8rem 0.3rem;
    font-style: italic;
}

/* Responsive: 3 columnas en desktop, 2 en tablet, 1 en móvil */
@media (max-width: 1600px) {
    .semaforo-matriz-proyectos {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 1200px) {
    .semaforo-matriz-proyectos {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .proyecto-box {
        padding: 1rem;
    }
    
    .fases-grid {
        gap: 0.6rem;
    }
}

@media (max-width: 768px) {
    .semaforo-matriz-proyectos {
        grid-template-columns: 1fr;
    }
    
    .fases-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .proyecto-titulo {
        font-size: 1rem;
        padding: 0.6rem;
    }
}
</style>
"""
            
            st.markdown(semaforo_css, unsafe_allow_html=True)
            
            # Mensaje informativo sobre la distribución
            num_proyectos = len(proyectos_seleccionados)
            if num_proyectos > 3:
                filas = (num_proyectos + 2) // 3
                st.info(f"📐 **Distribución visual**: {num_proyectos} proyectos organizados en {filas} fila{'s' if filas > 1 else ''} (máximo 3 proyectos por fila)")
            
            # Construir HTML de la matriz
            matriz_html = "<div class='semaforo-matriz-proyectos'>"
            
            for proy_id in proyectos_seleccionados:
                proy_nombre = proyectos_nombres[proy_id]
                proy_data = ebct_comparacion_full[ebct_comparacion_full['ID_Proyecto'] == proy_id]
                
                matriz_html += f"""
<div class='proyecto-box'>
    <div class='proyecto-titulo'>{proy_nombre}</div>
    <div class='fases-grid'>"""
                
                # Generar columnas por cada fase
                for fase in fases_ebct:
                    fase_color = fase_colors.get(fase, "#666")
                    fase_data = proy_data[proy_data.get('Fase_Normalizada', proy_data.get('Fase', '')) == fase]
                    
                    # Nombre corto de fase para la columna
                    fase_short = fase.replace("Fase ", "F")
                    
                    matriz_html += f"""
        <div class='fase-columna' style='border-top-color: {fase_color};'>
            <div class='fase-nombre' style='background: {fase_color};'>{fase_short}</div>
            <div class='ids-container-fase'>"""
                    
                    if len(fase_data) == 0:
                        matriz_html += """
                <div class='empty-fase-semaforo'>Sin datos</div>"""
                    else:
                        # Agregar cada característica
                        for _, row in fase_data.iterrows():
                            char_id = row.get('ID_Caracteristica', row.get('id', '?'))
                            estado_color = row.get('Estado_Color', 2)
                            nombre = row.get('Caracteristica', 'Sin nombre')
                            
                            # Determinar clase de color
                            if estado_color == 3:
                                color_class = "verde"
                                estado_texto = "� Verde (Cumple)"
                            elif estado_color == 2:
                                color_class = "amarillo"
                                estado_texto = "🟡 Amarillo (En desarrollo)"
                            else:
                                color_class = "rojo"
                                estado_texto = "� Rojo (No cumple)"
                            
                            # Tooltip con información
                            tooltip = f"""<strong>ID:</strong> {char_id}<br>
<strong>Característica:</strong> {nombre[:40]}...<br>
<strong>Estado:</strong> {estado_texto}<br>
<strong>Fase:</strong> {fase_short}"""
                            
                            matriz_html += f"""
                <div class='id-box-semaforo {color_class}'>
                    {char_id}
                    <span class='tooltip-semaforo'>{tooltip}</span>
                </div>"""
                    
                    matriz_html += """
            </div>
        </div>"""
                
                matriz_html += """
    </div>
</div>"""
            
            matriz_html += "</div>"
            
            # Renderizar matriz
            st.markdown(matriz_html, unsafe_allow_html=True)
            
            # Leyenda
            st.markdown("""
            <div style='display: flex; gap: 2rem; justify-content: center; margin-top: 1rem; padding: 1rem; background: #f5f5f5; border-radius: 8px;'>
                <div><strong>🟢 Verde:</strong> Cumple satisfactoriamente</div>
                <div><strong>🟡 Amarillo:</strong> En desarrollo/progreso</div>
                <div><strong>🔴 Rojo:</strong> No cumple - Requiere atención</div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ Selecciona al menos 2 proyectos para realizar comparaciones")
    
    # ============================================================================
    # TAB 3: VISTA INDIVIDUAL
    # ============================================================================
    with tab_individual:
        st.markdown("## 🔍 Vista Detallada por Proyecto")
        
        proyecto_seleccionado = st.selectbox(
            "Selecciona un proyecto para ver detalles",
            options=df_indice['ID_Proyecto'].tolist(),
            format_func=lambda x: f"{x} - {df_indice[df_indice['ID_Proyecto']==x]['Nombre_Proyecto'].values[0]}"
        )
        
        if proyecto_seleccionado:
            # Filtrar datos del proyecto
            proyecto_info = df_indice[df_indice['ID_Proyecto'] == proyecto_seleccionado].iloc[0]
            proyecto_irl = df_irl[df_irl['ID_Proyecto'] == proyecto_seleccionado]
            proyecto_ebct = df_ebct[df_ebct['ID_Proyecto'] == proyecto_seleccionado]
            proyecto_acciones = df_acciones[df_acciones['ID_Proyecto'] == proyecto_seleccionado]
            proyecto_indicadores = df_indicadores[df_indicadores['ID_Proyecto'] == proyecto_seleccionado].iloc[0]
            
            # ===== HEADER CON TARJETAS PROFESIONALES =====
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1565C0, #1E88E5); padding: 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <h2 style='color: white; margin: 0; font-size: 2rem;'>📁 {proyecto_info['Nombre_Proyecto']}</h2>
                <p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.1rem;'>
                    <strong>ID:</strong> {proyecto_info['ID_Proyecto']} | 
                    <strong>Responsable:</strong> {proyecto_info['Responsable']} | 
                    <strong>Estado:</strong> {proyecto_info['Estado']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # ===== TARJETAS DE INDICADORES PRINCIPALES =====
            col_card1, col_card2, col_card3, col_card4, col_card5 = st.columns(5)
            
            with col_card1:
                irl_min = proyecto_irl['Nivel_Alcanzado'].min()
                irl_max = proyecto_irl['Nivel_Alcanzado'].max()
                irl_mean = proyecto_indicadores['Indicador_IRL_Promedio']
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #0288d1, #039be5); padding: 1.2rem; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <div style='font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem;'>🎯 IRL RANGO</div>
                    <div style='font-size: 2rem; font-weight: bold; margin: 0.3rem 0;'>{irl_min:.0f}-{irl_max:.0f}</div>
                    <div style='font-size: 0.8rem; opacity: 0.8;'>Media: {irl_mean:.1f}/9</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_card2:
                cumplimiento_ebct = proyecto_indicadores['Indicador_Cumplimiento_EBCT']
                color_ebct = '#2e7d32' if cumplimiento_ebct >= 70 else ('#f57c00' if cumplimiento_ebct >= 40 else '#c62828')
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {color_ebct}, {color_ebct}dd); padding: 1.2rem; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <div style='font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem;'>✅ CUMPLIMIENTO EBCT</div>
                    <div style='font-size: 2rem; font-weight: bold; margin: 0.3rem 0;'>{cumplimiento_ebct:.0f}%</div>
                    <div style='font-size: 0.8rem; opacity: 0.8;'>34 Características</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_card3:
                madurez = proyecto_indicadores['Indicador_Madurez_Global']
                color_mad = '#2e7d32' if madurez >= 70 else ('#f57c00' if madurez >= 40 else '#c62828')
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {color_mad}, {color_mad}dd); padding: 1.2rem; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <div style='font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem;'>🏆 MADUREZ GLOBAL</div>
                    <div style='font-size: 2rem; font-weight: bold; margin: 0.3rem 0;'>{madurez:.1f}%</div>
                    <div style='font-size: 0.8rem; opacity: 0.8;'>IRL 40% + EBCT 60%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_card4:
                # Obtener porcentaje verde (con compatibilidad hacia atrás)
                if 'Indicador_Caracteristicas_Verde' in proyecto_indicadores.index:
                    verdes_pct = proyecto_indicadores['Indicador_Caracteristicas_Verde']
                elif 'Porcentaje_Verde' in proyecto_indicadores.index:
                    verdes_pct = proyecto_indicadores['Porcentaje_Verde']
                else:
                    # Calcular si no existe
                    ebct_proy = df_ebct[df_ebct['ID_Proyecto'] == id_proyecto_seleccionado]
                    if 'Estado_Color' in ebct_proy.columns and len(ebct_proy) > 0:
                        verdes_pct = (len(ebct_proy[ebct_proy['Estado_Color'] == 3]) / len(ebct_proy) * 100)
                    else:
                        verdes_pct = 0
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #43a047, #66bb6a); padding: 1.2rem; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <div style='font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem;'>🟢 CARACTERÍSTICAS OK</div>
                    <div style='font-size: 2rem; font-weight: bold; margin: 0.3rem 0;'>{verdes_pct:.0f}%</div>
                    <div style='font-size: 0.8rem; opacity: 0.8;'>En verde</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_card5:
                presupuesto = proyecto_info['Presupuesto_Total']
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #7b1fa2, #9c27b0); padding: 1.2rem; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <div style='font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem;'>💰 PRESUPUESTO</div>
                    <div style='font-size: 1.5rem; font-weight: bold; margin: 0.3rem 0;'>${presupuesto:,.0f}</div>
                    <div style='font-size: 0.8rem; opacity: 0.8;'>Total asignado</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ===== INFORMACIÓN DE PLAN DE ACCIÓN =====
            st.markdown("### � Estado del Plan de Acción")
            
            if len(proyecto_acciones) > 0:
                # Calcular estadísticas de fechas
                from datetime import datetime, timedelta
                hoy = datetime.now()
                
                # Última actualización (usar fecha más reciente del índice)
                fecha_actualizacion = pd.to_datetime(proyecto_info.get('Fecha_Actualizacion', proyecto_info.get('Fecha_Inicio')))
                dias_desde_actualizacion = (hoy - fecha_actualizacion).days
                
                # Analizar fechas de acciones
                proyecto_acciones_copy = proyecto_acciones.copy()
                proyecto_acciones_copy['Fecha_Fin'] = pd.to_datetime(proyecto_acciones_copy['Fecha_Fin'])
                
                acciones_vencidas = 0
                acciones_proximas = 0
                dias_min_vencimiento = None
                
                for _, accion in proyecto_acciones_copy.iterrows():
                    if accion['Completado'] != 'Sí':
                        fecha_fin = accion['Fecha_Fin']
                        dias_restantes = (fecha_fin - hoy).days
                        
                        if dias_restantes < 0:
                            acciones_vencidas += 1
                        elif dias_restantes <= 30:
                            acciones_proximas += 1
                            if dias_min_vencimiento is None or dias_restantes < dias_min_vencimiento:
                                dias_min_vencimiento = dias_restantes
                
                total_acciones = len(proyecto_acciones)
                acciones_completadas = len(proyecto_acciones[proyecto_acciones['Completado'] == 'Sí'])
                
                col_plan1, col_plan2, col_plan3, col_plan4 = st.columns(4)
                
                with col_plan1:
                    st.metric(
                        "📅 Última Revisión",
                        f"Hace {dias_desde_actualizacion} días",
                        delta=fecha_actualizacion.strftime('%Y-%m-%d')
                    )
                
                with col_plan2:
                    st.metric(
                        "✅ Acciones Completadas",
                        f"{acciones_completadas}/{total_acciones}",
                        delta=f"{(acciones_completadas/total_acciones*100):.0f}%" if total_acciones > 0 else "0%"
                    )
                
                with col_plan3:
                    if acciones_vencidas > 0:
                        st.metric(
                            "⚠️ Acciones Vencidas",
                            f"{acciones_vencidas}",
                            delta="Requieren atención",
                            delta_color="inverse"
                        )
                    else:
                        st.metric(
                            "✨ Acciones Vencidas",
                            "0",
                            delta="Todo al día"
                        )
                
                with col_plan4:
                    if dias_min_vencimiento is not None and dias_min_vencimiento >= 0:
                        st.metric(
                            "⏰ Próximo Vencimiento",
                            f"{dias_min_vencimiento} días",
                            delta=f"{acciones_proximas} acción(es) próxima(s)"
                        )
                    elif acciones_vencidas == 0 and acciones_completadas == total_acciones:
                        st.metric(
                            "🎉 Estado",
                            "Completo",
                            delta="Todas las acciones finalizadas"
                        )
                    else:
                        st.metric(
                            "📊 Acciones Activas",
                            f"{total_acciones - acciones_completadas}",
                            delta="En progreso"
                        )
            else:
                st.info("📝 No hay acciones registradas en el plan")
            
            st.markdown("---")
            
            # ===== GRÁFICOS DE ANÁLISIS =====
            st.markdown("### 📊 Análisis de Indicadores")
            
            # Fila 1: Radar IRL, Pie EBCT, Radar EBCT por Fases
            col_graf1, col_graf2, col_graf3 = st.columns(3)
            
            with col_graf1:
                st.markdown("##### 🎯 IRL por Dimensión")
                st.caption("Escala: 1-9 (logro por dimensión)")
                fig_radar_irl = go.Figure()
                fig_radar_irl.add_trace(go.Scatterpolar(
                    r=proyecto_irl['Nivel_Alcanzado'].tolist(),
                    theta=proyecto_irl['Dimension'].tolist(),
                    fill='toself',
                    name='Nivel Alcanzado',
                    line_color='#0288d1',
                    fillcolor='rgba(2, 136, 209, 0.3)',
                    line_width=2
                ))
                fig_radar_irl.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, 
                            range=[0, 9],
                            tickmode='linear',
                            tick0=0,
                            dtick=1,
                            gridcolor='#e0e0e0'
                        ),
                        angularaxis=dict(gridcolor='#e0e0e0')
                    ),
                    showlegend=False,
                    height=350,
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig_radar_irl, use_container_width=True, key=f"radar_irl_ind_{proyecto_seleccionado}")
            
            with col_graf2:
                st.markdown("##### 🚦 Distribución EBCT")
                st.caption("Características por estado")
                
                # Contar estados usando Estado_Color
                verdes = len(proyecto_ebct[proyecto_ebct['Estado_Color'] == 3])
                amarillos = len(proyecto_ebct[proyecto_ebct['Estado_Color'] == 2])
                rojos = len(proyecto_ebct[proyecto_ebct['Estado_Color'] == 1])
                total = len(proyecto_ebct)
                
                if total > 0:
                    # Crear gráfico de pie con go.Figure (estilo comparativo)
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['� Verde', '🟡 Amarillo', '�🔴 Rojo'],
                        values=[verdes, amarillos, rojos],
                        hole=0.4,
                        marker=dict(
                            colors=['#2e7d32', '#f57c00', '#c62828'],
                            line=dict(color='white', width=2)
                        ),
                        textposition='outside',
                        textinfo='percent+label',
                        pull=[0.1 if verdes == max(verdes, amarillos, rojos) else 0,
                              0.1 if amarillos == max(verdes, amarillos, rojos) else 0,
                              0.1 if rojos == max(verdes, amarillos, rojos) else 0]
                    )])
                    
                    fig_pie.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05
                        ),
                        annotations=[dict(
                            text=f'{verdes}<br>Verdes',
                            x=0.5, y=0.5,
                            font_size=18,
                            font_color='#2e7d32',
                            showarrow=False
                        )]
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_ind_{proyecto_seleccionado}")
                else:
                    st.info("📊 No hay datos EBCT disponibles")
            
            with col_graf3:
                st.markdown("##### 🎯 Radar EBCT por Fases")
                st.caption("Cumplimiento % por fase")
                
                if len(proyecto_ebct) > 0:
                    # Preparar datos EBCT para radar (lógica Fase 2)
                    radar_df = proyecto_ebct.copy()
                    
                    # 🔍 DEBUG: Ver datos antes del radar
                    with st.expander("🔍 Debug Radar EBCT", expanded=False):
                        st.write(f"**Total registros:** {len(radar_df)}")
                        st.write(f"**Columnas:** {radar_df.columns.tolist()}")
                        st.write(f"**Valores únicos en Fase:** {radar_df['Fase'].unique().tolist()}")
                        st.write(f"**Tipo de dato Fase:** {radar_df['Fase'].dtype}")
                        st.write(f"**Valores únicos en Estado_Color:** {radar_df['Estado_Color'].unique().tolist()}")
                        st.write("**Primeras 5 filas:**")
                        st.dataframe(radar_df[['Fase', 'Estado_Color', 'ID_Caracteristica']].head())
                    
                    # Normalizar Fase a texto (puede venir como número o texto del Excel)
                    if radar_df['Fase'].dtype in ['int64', 'float64']:
                        # Si es numérico, convertir a texto
                        fase_mapping_radar = {
                            1: "Fase 1",
                            2: "Fase 2",
                            3: "Fase 3",
                            4: "Fase 4"
                        }
                        radar_df['Fase_Normalizada'] = radar_df['Fase'].map(fase_mapping_radar)
                    else:
                        # Si ya es texto, usarlo directamente
                        radar_df['Fase_Normalizada'] = radar_df['Fase'].astype(str)
                    
                    # Mapeo final a nombres completos
                    mapeo_fases_completo = {
                        "Fase 1": "Fase Incipiente",
                        "1": "Fase Incipiente",
                        "Fase 2": "Fase Validación y PI",
                        "2": "Fase Validación y PI",
                        "Fase 3": "Fase Preparación para Mercado",
                        "3": "Fase Preparación para Mercado",
                        "Fase 4": "Fase Internacionalización",
                        "4": "Fase Internacionalización"
                    }
                    radar_df['Fase_Final'] = radar_df['Fase_Normalizada'].map(mapeo_fases_completo).fillna(radar_df['Fase_Normalizada'])
                    
                    # Calcular cumplimiento por fase
                    fases_orden = [
                        "Fase Incipiente",
                        "Fase Validación y PI",
                        "Fase Preparación para Mercado",
                        "Fase Internacionalización"
                    ]
                    
                    cumplimiento_por_fase = []
                    for fase in fases_orden:
                        fase_data = radar_df[radar_df['Fase_Final'] == fase]
                        if len(fase_data) > 0:
                            verdes_fase = len(fase_data[fase_data['Estado_Color'] == 3])
                            cumplimiento = (verdes_fase / len(fase_data)) * 100
                        else:
                            cumplimiento = 0
                        cumplimiento_por_fase.append(cumplimiento)
                        cumplimiento_por_fase.append(cumplimiento)
                    
                    # Crear gráfico radar
                    fig_radar_ebct = go.Figure()
                    fig_radar_ebct.add_trace(go.Scatterpolar(
                        r=cumplimiento_por_fase,
                        theta=[f.replace('Fase ', 'F') for f in fases_orden],
                        fill='toself',
                        name='Cumplimiento',
                        line_color='#1f6b36',
                        fillcolor='rgba(31, 107, 54, 0.35)',
                        line_width=2
                    ))
                    
                    fig_radar_ebct.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                tickmode='linear',
                                tick0=0,
                                dtick=20,
                                ticksuffix='%',
                                gridcolor='#e0e0e0'
                            ),
                            angularaxis=dict(gridcolor='#e0e0e0')
                        ),
                        showlegend=False,
                        height=350,
                        margin=dict(l=40, r=40, t=40, b=40)
                    )
                    
                    st.plotly_chart(fig_radar_ebct, use_container_width=True, key=f"radar_ebct_ind_{proyecto_seleccionado}")
                else:
                    st.info("📊 No hay datos EBCT disponibles")
            
            st.markdown("---")
            
            # ===== TABLAS DETALLADAS PROFESIONALES =====
            st.markdown("###  Información Detallada")
            
            tab1, tab2, tab3 = st.tabs(["📊 Niveles IRL", "🎯 Características EBCT", "� Plan de Acción"])
            
            with tab1:
                st.markdown("#### 🎯 Detalle de Niveles IRL por Dimensión")
                # Preparar datos con formato mejorado
                df_irl_display = proyecto_irl.copy()
                df_irl_display['Progreso'] = (df_irl_display['Nivel_Alcanzado'] / 9 * 100).round(1)
                df_irl_display = df_irl_display[['Dimension', 'Nivel_Alcanzado', 'Progreso']]
                df_irl_display.columns = ['Dimensión', 'Nivel (1-9)', '% Progreso']
                
                # Aplicar estilos con gradientes
                styled_irl = df_irl_display.style.background_gradient(
                    subset=['Nivel (1-9)'], 
                    cmap='YlGnBu',
                    vmin=1,
                    vmax=9
                ).background_gradient(
                    subset=['% Progreso'],
                    cmap='RdYlGn',
                    vmin=0,
                    vmax=100
                ).format({
                    'Nivel (1-9)': '{:.1f}',
                    '% Progreso': '{:.1f}%'
                }).set_properties(**{
                    'text-align': 'center',
                    'font-size': '14px',
                    'border': '1px solid #ddd'
                }).set_table_styles([
                    {'selector': 'th', 'props': [
                        ('background-color', '#1565C0'),
                        ('color', 'white'),
                        ('font-weight', 'bold'),
                        ('text-align', 'center'),
                        ('padding', '12px'),
                        ('border', '1px solid #0d47a1')
                    ]},
                    {'selector': 'td', 'props': [
                        ('padding', '10px'),
                        ('border', '1px solid #e0e0e0')
                    ]},
                    {'selector': 'tr:hover', 'props': [
                        ('background-color', '#e3f2fd')
                    ]}
                ])
                
                st.dataframe(styled_irl, use_container_width=True, hide_index=True)
                
                # Resumen estadístico
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("📊 Promedio", f"{df_irl_display['Nivel (1-9)'].mean():.1f}")
                with col_stat2:
                    st.metric("⬆️ Máximo", f"{df_irl_display['Nivel (1-9)'].max():.1f}")
                with col_stat3:
                    st.metric("⬇️ Mínimo", f"{df_irl_display['Nivel (1-9)'].min():.1f}")
                with col_stat4:
                    st.metric("📈 Desv. Est.", f"{df_irl_display['Nivel (1-9)'].std():.2f}")
            
            with tab2:
                st.markdown("#### 🧭 Detalle de Características EBCT")
                
                # Preparar datos con formato mejorado
                df_ebct_display = proyecto_ebct.copy()
                df_ebct_display = df_ebct_display[[
                    'ID_Caracteristica', 'Caracteristica', 'Fase', 'Estado_Actual'
                ]]
                df_ebct_display.columns = ['ID', 'Característica', 'Fase', 'Estado']
                
                # Función para colorear filas según estado
                def colorear_estado(row):
                    if '🟢' in str(row['Estado']):
                        return ['background-color: #c8e6c9'] * len(row)
                    elif '🟡' in str(row['Estado']):
                        return ['background-color: #fff9c4'] * len(row)
                    else:
                        return ['background-color: #ffcdd2'] * len(row)
                
                # Aplicar estilos
                styled_ebct = df_ebct_display.style.apply(
                    colorear_estado, axis=1
                ).set_properties(**{
                    'text-align': 'left',
                    'font-size': '13px',
                    'border': '1px solid #ddd',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [
                        ('background-color', '#1565C0'),
                        ('color', 'white'),
                        ('font-weight', 'bold'),
                        ('text-align', 'center'),
                        ('padding', '12px'),
                        ('border', '1px solid #0d47a1')
                    ]},
                    {'selector': 'td', 'props': [
                        ('border', '1px solid #e0e0e0')
                    ]},
                    {'selector': 'tr:hover', 'props': [
                        ('opacity', '0.8'),
                        ('transform', 'scale(1.01)')
                    ]}
                ])
                
                st.dataframe(styled_ebct, use_container_width=True, hide_index=True, height=500)
                
                # Resumen por fase
                st.markdown("##### 📊 Distribución por Fase")
                col_fase1, col_fase2, col_fase3, col_fase4 = st.columns(4)
                
                for i, (col, fase_num) in enumerate([(col_fase1, 1), (col_fase2, 2), (col_fase3, 3), (col_fase4, 4)], 1):
                    chars_fase = df_ebct_display[df_ebct_display['Fase'] == fase_num]
                    verdes = len([x for x in chars_fase['Estado'] if '🟢' in str(x)])
                    total = len(chars_fase)
                    pct = (verdes/total*100) if total > 0 else 0
                    
                    with col:
                        st.metric(
                            f"Fase {fase_num}",
                            f"{verdes}/{total}",
                            delta=f"{pct:.0f}% OK"
                        )
            
            with tab3:
                st.markdown("#### 📅 Detalle del Plan de Acción")
                
                if len(proyecto_acciones) > 0:
                    from datetime import datetime
                    hoy = datetime.now()
                    
                    # Preparar datos con cálculos de fechas
                    df_acciones_display = proyecto_acciones.copy()
                    df_acciones_display['Fecha_Inicio'] = pd.to_datetime(df_acciones_display['Fecha_Inicio'])
                    df_acciones_display['Fecha_Fin'] = pd.to_datetime(df_acciones_display['Fecha_Fin'])
                    
                    # Calcular días restantes o vencimiento
                    def calcular_estado_fecha(row):
                        if row['Completado'] == 'Sí':
                            return '✅ Completado'
                        
                        dias_restantes = (row['Fecha_Fin'] - hoy).days
                        
                        if dias_restantes < 0:
                            return f'🔴 Vencido ({abs(dias_restantes)} días)'
                        elif dias_restantes == 0:
                            return '🟡 Vence hoy'
                        elif dias_restantes <= 7:
                            return f'🟡 {dias_restantes} días'
                        else:
                            return f'🟢 {dias_restantes} días'
                    
                    df_acciones_display['Estado_Fecha'] = df_acciones_display.apply(calcular_estado_fecha, axis=1)
                    
                    # Formatear fechas
                    df_acciones_display['Fecha_Inicio_Fmt'] = df_acciones_display['Fecha_Inicio'].dt.strftime('%Y-%m-%d')
                    df_acciones_display['Fecha_Fin_Fmt'] = df_acciones_display['Fecha_Fin'].dt.strftime('%Y-%m-%d')
                    
                    # Seleccionar columnas (usar nombres reales del Excel)
                    df_acciones_display = df_acciones_display[[
                        'Descripcion', 'Responsable', 'Fecha_Inicio_Fmt', 
                        'Fecha_Fin_Fmt', 'Estado_Fecha', 'Completado'
                    ]]
                    df_acciones_display.columns = [
                        'Acción', 'Responsable', 'Inicio', 'Fin', 'Estado Plazo', 'Completado'
                    ]
                    
                    # Función para colorear según estado
                    def colorear_accion(row):
                        if row['Completado'] == 'Sí':
                            return ['background-color: #c8e6c9'] * len(row)
                        elif '🔴' in str(row['Estado Plazo']):
                            return ['background-color: #ffcdd2'] * len(row)
                        elif '🟡' in str(row['Estado Plazo']):
                            return ['background-color: #fff9c4'] * len(row)
                        else:
                            return ['background-color: #e3f2fd'] * len(row)
                    
                    # Aplicar estilos
                    styled_acciones = df_acciones_display.style.apply(
                        colorear_accion, axis=1
                    ).set_properties(**{
                        'text-align': 'left',
                        'font-size': '13px',
                        'border': '1px solid #ddd',
                        'padding': '8px'
                    }).set_table_styles([
                        {'selector': 'th', 'props': [
                            ('background-color', '#1565C0'),
                            ('color', 'white'),
                            ('font-weight', 'bold'),
                            ('text-align', 'center'),
                            ('padding', '12px'),
                            ('border', '1px solid #0d47a1')
                        ]},
                        {'selector': 'td', 'props': [
                            ('border', '1px solid #e0e0e0')
                        ]},
                        {'selector': 'tr:hover', 'props': [
                            ('opacity', '0.8')
                        ]}
                    ])
                    
                    st.dataframe(styled_acciones, use_container_width=True, hide_index=True, height=400)
                    
                    # Alertas importantes
                    vencidas = len([x for x in df_acciones_display['Estado Plazo'] if '🔴' in str(x)])
                    proximas = len([x for x in df_acciones_display['Estado Plazo'] if '🟡' in str(x) and 'días' in str(x)])
                    
                    if vencidas > 0:
                        st.error(f"⚠️ **ATENCIÓN**: Tienes {vencidas} acción(es) vencida(s) que requieren atención inmediata.")
                    
                    if proximas > 0:
                        st.warning(f"⏰ **RECORDATORIO**: Tienes {proximas} acción(es) próxima(s) a vencer en los próximos 7 días.")
                    
                    if vencidas == 0 and proximas == 0:
                        completadas = len(df_acciones_display[df_acciones_display['Completado'] == 'Sí'])
                        if completadas == len(df_acciones_display):
                            st.success("🎉 ¡Excelente! Todas las acciones del plan han sido completadas.")
                        else:
                            st.info("✅ Todas las acciones están dentro del plazo establecido.")
                
                else:
                    st.info("📝 No hay acciones registradas en el plan de acción para este proyecto.")
else:
    st.info("📂 No hay datos cargados. Descarga la plantilla, compléta la información y cárgala para visualizar los indicadores.")
