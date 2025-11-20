"""
Página 05: Diagnóstico y Plan de Acción
Integra resultados de Fase 1 (IRL) y Fase 2 (EBCT) para generar un plan estratégico
"""

import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Configuración de la página
st.set_page_config(
    page_title="Diagnóstico y Plan de Acción",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Diagnóstico y Plan de Acción")
st.markdown("### Definir requerimientos de recursos humanos, tecnología y financiamiento")

st.markdown("---")

# ============================================================================
# SECCIÓN 1: DIAGNÓSTICO - Resultados de Fase 1 y Fase 2
# ============================================================================

st.markdown("## 🔍 Diagnóstico General")

col_fase1, col_fase2 = st.columns(2)

with col_fase1:
    st.markdown("### 📊 Fase 1: Niveles IRL")
    
    # Obtener niveles IRL del session_state
    irl_scores = st.session_state.get("irl_scores", {})
    
    if irl_scores:
        irl_data = []
        for dimension, nivel in irl_scores.items():
            porcentaje = (nivel / 9) * 100
            if porcentaje >= 70:
                estado = "✓ Avanzado"
                color = "#1565c0"
            elif porcentaje >= 40:
                estado = "◐ En Progreso"
                color = "#f57c00"
            else:
                estado = "○ Inicial"
                color = "#757575"
            
            irl_data.append({
                'Dimensión': dimension,
                'Nivel': f"{nivel}/9",
                'Estado': estado,
                'Color': color
            })
        
        # Mostrar tabla con colores
        st.markdown("<div style='max-height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
        for item in irl_data:
            st.markdown(f"""
                <div style="background: white; border-left: 4px solid {item['Color']}; 
                            padding: 0.8rem; margin-bottom: 0.5rem; border-radius: 6px;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: {item['Color']};">{item['Dimensión']}</strong>
                            <span style="color: #666; margin-left: 1rem;">{item['Estado']}</span>
                        </div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: {item['Color']};">
                            {item['Nivel']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No hay datos de IRL. Complete la Fase 1 primero.")

with col_fase2:
    st.markdown("### 🎯 Fase 2: Características Críticas EBCT")
    st.caption("*Características en ROJO (No cumple) y AMARILLO (En desarrollo)*")
    
    # Obtener características de EBCT del session_state
    semaforo_df = st.session_state.get("semaforo_df", None)
    
    caracteristicas_criticas = []
    
    # Obtener características críticas (Rojas y Amarillas)
    if semaforo_df is not None and not semaforo_df.empty:
        for _, row in semaforo_df.iterrows():
            estado_semaforo = row.get('EstadoSemaforo', '')
            
            # Filtrar solo Rojas y Amarillas
            if '🔴' in estado_semaforo or '🟡' in estado_semaforo:
                # Determinar prioridad: Rojo = 1, Amarillo = 2
                prioridad = 1 if '🔴' in estado_semaforo else 2
                
                caracteristicas_criticas.append({
                    'id': row.get('id', 0),
                    'Categoría': row.get('Fase', 'N/A'),
                    'Característica': row.get('Característica', ''),
                    'Dimensiones': row.get('Dimensiones', ''),
                    'Estado': estado_semaforo,
                    'Prioridad': prioridad,
                    'Score': row.get('Score', 0.0),
                    'Peso': row.get('Peso', 1)
                })
    
    # Ordenar por prioridad (rojas primero)
    caracteristicas_criticas = sorted(caracteristicas_criticas, key=lambda x: x['Prioridad'])
    
    if caracteristicas_criticas:
        st.info(f"📌 **{len(caracteristicas_criticas)} características** requieren atención")
        
        # Contar por estado
        rojas = sum(1 for c in caracteristicas_criticas if c['Prioridad'] == 1)
        amarillas = sum(1 for c in caracteristicas_criticas if c['Prioridad'] == 2)
        
        col_r, col_a = st.columns(2)
        with col_r:
            st.metric("🔴 No cumple", rojas)
        with col_a:
            st.metric("🟡 En desarrollo", amarillas)
        
        # Mostrar características críticas en un expander desplegable
        with st.expander(f"👁️ Ver detalle de las {len(caracteristicas_criticas)} características críticas", expanded=False):
            st.markdown("<div style='max-height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
            for item in caracteristicas_criticas:
                color = "#c62828" if item['Prioridad'] == 1 else "#f57c00"
                st.markdown(f"""
                    <div style="background: white; border-left: 4px solid {color}; 
                                padding: 0.8rem; margin-bottom: 0.5rem; border-radius: 6px;
                                box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                        <div style="color: {color}; font-weight: 600; margin-bottom: 0.3rem;">
                            {item['Estado']} - {item['Categoría']}
                        </div>
                        <div style="color: #333; font-size: 0.9rem; margin-bottom: 0.3rem;">
                            <strong>ID {item['id']}:</strong> {item['Característica']}
                        </div>
                        <div style="color: #666; font-size: 0.8rem;">
                            {item['Dimensiones']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if semaforo_df is not None and not semaforo_df.empty:
            st.success("✅ No hay características críticas. ¡Excelente trabajo!")
        else:
            st.warning("⚠️ No hay datos de EBCT. Complete la Fase 2 primero.")

st.markdown("---")

# ============================================================================
# SECCIÓN 2: PLAN DE ACCIÓN
# ============================================================================

st.markdown("## 📝 Plan de Acción")
st.caption("*Define acciones, recursos, presupuesto y cronograma para cada característica crítica*")

# Inicializar tipos de recursos personalizados en session_state
if 'tipos_recursos_custom' not in st.session_state:
    st.session_state.tipos_recursos_custom = []

# Opciones de tipo: predefinidas
tipos_predefinidos = [
    "Tecnológico", "Humano", "Infraestructura", "Capacitación", 
    "Consultoría", "Materiales", "Software", "Hardware", 
    "Equipamiento", "Servicios", "Licencias", "I+D", "Innovación", "Otro"
]

# Sección de gestión de tipos de recursos (colapsable)
with st.expander("⚙️ Gestionar Tipos de Recursos Personalizados", expanded=False):
    st.markdown("##### 📋 Tipos de Recursos Disponibles")
    
    col_tipos_pred, col_tipos_custom = st.columns(2)
    
    with col_tipos_pred:
        st.markdown("**Tipos Predefinidos:**")
        st.info("🏷️ " + " | ".join(tipos_predefinidos[:7]))
        st.info("🏷️ " + " | ".join(tipos_predefinidos[7:]))
    
    with col_tipos_custom:
        st.markdown("**Tipos Personalizados:**")
        if st.session_state.tipos_recursos_custom:
            for idx, tipo in enumerate(st.session_state.tipos_recursos_custom):
                col_tipo_display = st.columns([4, 1])
                with col_tipo_display[0]:
                    st.markdown(f"🏷️ **{tipo}**")
                with col_tipo_display[1]:
                    if st.button("🗑️", key=f"del_tipo_global_{idx}", help=f"Eliminar '{tipo}'"):
                        st.session_state.tipos_recursos_custom.pop(idx)
                        st.success(f"✅ Tipo '{tipo}' eliminado")
                        st.rerun()
        else:
            st.info("No hay tipos personalizados. Agrega uno abajo.")
    
    st.markdown("---")
    st.markdown("##### ➕ Agregar Nuevo Tipo de Recurso")
    
    col_new_tipo = st.columns([3, 1])
    with col_new_tipo[0]:
        nuevo_tipo_recurso = st.text_input(
            "Nombre del nuevo tipo de recurso",
            placeholder="Ej: Propiedad Intelectual, Marketing, Certificaciones...",
            key="input_nuevo_tipo_global"
        )
    with col_new_tipo[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Crear Tipo", use_container_width=True, key="btn_crear_tipo_global", type="primary"):
            tipos_disponibles = tipos_predefinidos + st.session_state.tipos_recursos_custom
            if nuevo_tipo_recurso and nuevo_tipo_recurso not in tipos_disponibles:
                st.session_state.tipos_recursos_custom.append(nuevo_tipo_recurso)
                st.success(f"✅ Tipo '{nuevo_tipo_recurso}' creado exitosamente")
                st.rerun()
            elif nuevo_tipo_recurso in tipos_disponibles:
                st.warning("⚠️ Este tipo ya existe")
            else:
                st.warning("⚠️ Ingrese el nombre del tipo")

# Inicializar session_state para el plan de acción
if 'plan_accion' not in st.session_state:
    st.session_state.plan_accion = []

# Si hay características críticas, permitir agregar acciones
if caracteristicas_criticas:
    
    # Selector de característica
    st.markdown("### ➕ Agregar Acción al Plan")
    
    col_select, col_add = st.columns([3, 1])
    
    with col_select:
        opciones_caracteristicas = [
            f"{item['Estado']} | ID {item['id']} - {item['Característica'][:60]}..."
            for item in caracteristicas_criticas
        ]
        caracteristica_seleccionada = st.selectbox(
            "Selecciona la característica a atender",
            options=range(len(caracteristicas_criticas)),
            format_func=lambda x: opciones_caracteristicas[x],
            key="select_caracteristica"
        )
    
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Nueva Acción", use_container_width=True, type="primary"):
            st.session_state.show_form = True
    
    # Formulario para agregar acción
    if st.session_state.get('show_form', False):
        # Inicializar lista de recursos si no existe
        if 'temp_recursos' not in st.session_state:
            st.session_state.temp_recursos = []
        
        with st.form("form_accion"):
            st.markdown("#### 📋 Detalles de la Acción")
            
            caract_info = caracteristicas_criticas[caracteristica_seleccionada]
            st.info(f"**ID {caract_info['id']}**: {caract_info['Característica']}")
            st.caption(f"**Fase**: {caract_info['Categoría']} | **Dimensiones**: {caract_info['Dimensiones']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                descripcion_accion = st.text_area(
                    "Descripción de la acción",
                    placeholder="Describe la acción a realizar...",
                    height=100
                )
                
                responsable = st.text_input(
                    "👤 Recurso humano responsable",
                    placeholder="Nombre del responsable"
                )
            
            with col2:
                presupuesto = st.number_input(
                    "💰 Presupuesto estimado (USD)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f"
                )
                
                col_fecha1, col_fecha2 = st.columns(2)
                with col_fecha1:
                    fecha_inicio = st.date_input(
                        "📅 Fecha inicio",
                        value=datetime.now()
                    )
                with col_fecha2:
                    fecha_fin = st.date_input(
                        "📅 Fecha fin",
                        value=datetime.now() + timedelta(days=30)
                    )
            
            col_submit, col_cancel = st.columns([1, 1])
            with col_submit:
                submitted = st.form_submit_button("✅ Guardar Acción", use_container_width=True, type="primary")
            with col_cancel:
                cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                # Validar que todos los campos estén llenos
                if not descripcion_accion or not responsable:
                    st.error("⚠️ La descripción y el responsable son obligatorios")
                elif fecha_fin < fecha_inicio:
                    st.error("⚠️ La fecha de fin debe ser posterior a la fecha de inicio")
                else:
                    # Agregar acción al plan
                    nueva_accion = {
                        'id': len(st.session_state.plan_accion) + 1,
                        'caracteristica_id': caract_info['id'],
                        'caracteristica': caract_info['Característica'],
                        'categoria': caract_info['Categoría'],
                        'dimensiones': caract_info['Dimensiones'],
                        'estado_inicial': caract_info['Estado'],
                        'score_inicial': caract_info['Score'],
                        'peso': caract_info['Peso'],
                        'descripcion': descripcion_accion,
                        'responsable': responsable,
                        'recursos': st.session_state.temp_recursos.copy(),  # Lista de recursos
                        'presupuesto': presupuesto,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'duracion_dias': (fecha_fin - fecha_inicio).days,
                        'completado': False,
                        'avance_porcentaje': 0
                    }
                    st.session_state.plan_accion.append(nueva_accion)
                    st.session_state.show_form = False
                    st.session_state.temp_recursos = []  # Limpiar recursos temporales
                    st.success("✅ Acción agregada correctamente")
                    st.rerun()
            
            if cancelled:
                st.session_state.show_form = False
                st.session_state.temp_recursos = []  # Limpiar recursos temporales
                st.rerun()
        
        # SECCIÓN FUERA DEL FORM: Agregar recursos dinámicamente
        st.markdown("---")
        st.markdown("#### 🛠️ Recursos Necesarios")
        
        # Usar los tipos globales (predefinidos + personalizados)
        tipos_disponibles = tipos_predefinidos + st.session_state.tipos_recursos_custom
        
        st.caption(f"📋 {len(tipos_disponibles)} tipos de recursos disponibles (usa el expander de arriba para agregar más)")
        
        st.markdown("---")
        
        # Formulario para agregar recursos
        col_add_recurso = st.columns([2, 2, 1, 1])
        with col_add_recurso[0]:
            nuevo_recurso_nombre = st.text_input(
                "Nombre del recurso",
                placeholder="Ej: Servidor AWS EC2, Patente, Investigador...",
                key="nuevo_recurso_nombre"
            )
        with col_add_recurso[1]:
            nuevo_recurso_tipo = st.selectbox(
                "Tipo de recurso",
                options=tipos_disponibles,
                key="nuevo_recurso_tipo"
            )
        with col_add_recurso[2]:
            nuevo_recurso_costo = st.number_input(
                "Costo (USD)",
                min_value=0.0,
                step=50.0,
                format="%.2f",
                key="nuevo_recurso_costo"
            )
        with col_add_recurso[3]:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_agregar_recurso = st.button("➕ Agregar", use_container_width=True, key="btn_add_recurso")
        
        # Si selecciona "Otro", mostrar campo para especificar nuevo tipo
        tipo_final = nuevo_recurso_tipo
        if nuevo_recurso_tipo == "Otro":
            st.markdown("##### 🔖 Especificar Nuevo Tipo de Recurso")
            col_otro_tipo = st.columns([3, 2])
            with col_otro_tipo[0]:
                nuevo_tipo_especificado = st.text_input(
                    "Especifique el tipo de recurso",
                    placeholder="Ej: Propiedad Intelectual, Marketing Digital, Certificación...",
                    key="otro_tipo_especificado"
                )
            with col_otro_tipo[1]:
                guardar_tipo_nuevo = st.checkbox(
                    "💾 Guardar como tipo permanente",
                    value=True,
                    help="Si activa esta opción, el nuevo tipo quedará disponible para futuras acciones",
                    key="guardar_tipo_permanente"
                )
            
            if nuevo_tipo_especificado:
                tipo_final = nuevo_tipo_especificado
                st.info(f"✅ Se usará el tipo: **{nuevo_tipo_especificado}**")
        
        # Procesar el botón de agregar
        if btn_agregar_recurso:
            if not nuevo_recurso_nombre:
                st.warning("⚠️ Ingrese el nombre del recurso")
            elif nuevo_recurso_tipo == "Otro" and not nuevo_tipo_especificado:
                st.warning("⚠️ Debe especificar el tipo de recurso cuando selecciona 'Otro'")
            else:
                # Si es un tipo nuevo y se marcó para guardar, agregarlo a tipos personalizados
                if nuevo_recurso_tipo == "Otro" and guardar_tipo_nuevo and nuevo_tipo_especificado:
                    todos_tipos = tipos_predefinidos + st.session_state.tipos_recursos_custom
                    if nuevo_tipo_especificado not in todos_tipos:
                        st.session_state.tipos_recursos_custom.append(nuevo_tipo_especificado)
                        st.success(f"✅ Tipo '{nuevo_tipo_especificado}' guardado permanentemente")
                
                # Agregar el recurso
                st.session_state.temp_recursos.append({
                    'nombre': nuevo_recurso_nombre,
                    'tipo': tipo_final,
                    'costo': nuevo_recurso_costo
                })
                st.rerun()
        
        # Mostrar recursos agregados
        if st.session_state.temp_recursos:
            st.markdown("##### 📋 Recursos Agregados:")
            for idx, recurso in enumerate(st.session_state.temp_recursos):
                col_recurso = st.columns([3, 2, 2, 1])
                with col_recurso[0]:
                    st.markdown(f"**{recurso['nombre']}**")
                with col_recurso[1]:
                    st.markdown(f"🏷️ {recurso['tipo']}")
                with col_recurso[2]:
                    st.markdown(f"💰 ${recurso['costo']:,.2f}")
                with col_recurso[3]:
                    if st.button("🗑️", key=f"del_recurso_{idx}", help="Eliminar recurso"):
                        st.session_state.temp_recursos.pop(idx)
                        st.rerun()
            
            # Mostrar total de recursos
            total_recursos = sum(r['costo'] for r in st.session_state.temp_recursos)
            st.info(f"💰 **Total recursos**: ${total_recursos:,.2f} USD | 📦 **{len(st.session_state.temp_recursos)} recursos** agregados")

st.markdown("---")

# ============================================================================
# SECCIÓN 3: TABLA DE ACCIONES DEL PLAN
# ============================================================================

if st.session_state.plan_accion:
    st.markdown("### 📊 Acciones Registradas en el Plan")
    
    # Crear DataFrame
    df_plan = pd.DataFrame(st.session_state.plan_accion)
    
    # Calcular totales
    total_acciones = len(df_plan)
    presupuesto_total = df_plan['presupuesto'].sum()
    acciones_completadas = df_plan['completado'].sum()
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("📋 Total Acciones", total_acciones)
    with col_m2:
        st.metric("✅ Completadas", f"{acciones_completadas}/{total_acciones}")
    with col_m3:
        st.metric("💰 Presupuesto Total", f"${presupuesto_total:,.2f}")
    with col_m4:
        duracion_promedio = df_plan['duracion_dias'].mean()
        st.metric("⏱️ Duración Promedio", f"{duracion_promedio:.0f} días")
    
    st.markdown("---")
    
    # ============================================================================
    # GESTIÓN DE PROGRESO POR ACCIÓN
    # ============================================================================
    
    st.markdown("#### 📈 Gestión de Progreso")
    st.caption("*Actualiza el avance de cada acción para llevar las características a VERDE*")
    
    # Mostrar tabla de acciones con gestión de progreso
    for idx, accion in enumerate(st.session_state.plan_accion):
        with st.expander(
            f"{'✅' if accion['completado'] else '⏳'} ID {accion['id']}: {accion['caracteristica'][:50]}... ({accion['avance_porcentaje']}%)",
            expanded=False
        ):
            col_info, col_gestion = st.columns([1.5, 1])
            
            with col_info:
                # Formatear recursos
                recursos_text = ""
                if isinstance(accion['recursos'], list):
                    if accion['recursos']:
                        recursos_text = "\n"
                        for recurso in accion['recursos']:
                            recursos_text += f"   • {recurso['nombre']} ({recurso['tipo']}) - ${recurso['costo']:,.2f}\n"
                        total_recursos = sum(r['costo'] for r in accion['recursos'])
                        recursos_text += f"   **Total recursos**: ${total_recursos:,.2f}"
                    else:
                        recursos_text = "Sin recursos especificados"
                else:
                    # Compatibilidad con formato antiguo (texto)
                    recursos_text = accion['recursos'] if accion['recursos'] else "Sin recursos especificados"
                
                st.markdown(f"""
                    **📌 Característica ID**: {accion['caracteristica_id']}  
                    **🎯 Fase**: {accion['categoria']}  
                    **🔹 Dimensiones**: {accion['dimensiones']}  
                    **📊 Estado Inicial**: {accion['estado_inicial']}  
                    **📝 Acción**: {accion['descripcion']}  
                    **👤 Responsable**: {accion['responsable']}  
                    **🛠️ Recursos**: {recursos_text}  
                    **💰 Presupuesto Total**: ${accion['presupuesto']:,.2f}  
                    **📅 Periodo**: {accion['fecha_inicio']} → {accion['fecha_fin']}
                """)
            
            with col_gestion:
                st.markdown("##### 🎯 Actualizar Progreso")
                
                # Slider de avance
                nuevo_avance = st.slider(
                    "% Avance",
                    min_value=0,
                    max_value=100,
                    value=accion['avance_porcentaje'],
                    step=5,
                    key=f"avance_{accion['id']}"
                )
                
                # Checkbox de completado
                nuevo_completado = st.checkbox(
                    "✅ Marcar como completado",
                    value=accion['completado'],
                    key=f"completado_{accion['id']}"
                )
                
                # Botón para actualizar
                if st.button("💾 Guardar Progreso", key=f"btn_save_{accion['id']}", use_container_width=True):
                    st.session_state.plan_accion[idx]['avance_porcentaje'] = nuevo_avance
                    st.session_state.plan_accion[idx]['completado'] = nuevo_completado
                    
                    # Si está completado al 100%, automáticamente marcar como completado
                    if nuevo_avance == 100:
                        st.session_state.plan_accion[idx]['completado'] = True
                    
                    st.success(f"✅ Progreso actualizado: {nuevo_avance}%")
                    st.rerun()
                
                # Indicador visual de progreso
                if nuevo_avance >= 80:
                    color_progreso = "#2e7d32"
                    emoji = "🟢"
                elif nuevo_avance >= 50:
                    color_progreso = "#f57c00"
                    emoji = "🟡"
                else:
                    color_progreso = "#c62828"
                    emoji = "🔴"
                
                st.markdown(f"""
                    <div style="background: linear-gradient(90deg, {color_progreso} {nuevo_avance}%, #e0e0e0 {nuevo_avance}%);
                                padding: 0.5rem; border-radius: 8px; text-align: center; 
                                color: white; font-weight: bold; margin-top: 0.5rem;">
                        {emoji} {nuevo_avance}% Avance
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabla resumen
    st.markdown("#### 📋 Resumen Tabular")
    
    # Preparar datos para mostrar recursos de forma resumida
    df_display = df_plan.copy()
    df_display['recursos_count'] = df_display['recursos'].apply(
        lambda x: len(x) if isinstance(x, list) else (1 if x else 0)
    )
    df_display['recursos_total'] = df_display['recursos'].apply(
        lambda x: sum(r['costo'] for r in x) if isinstance(x, list) else 0
    )
    
    st.dataframe(
        df_display[[
            'id', 'caracteristica_id', 'categoria', 'caracteristica', 'descripcion', 
            'responsable', 'recursos_count', 'recursos_total', 'presupuesto', 
            'fecha_inicio', 'fecha_fin', 'avance_porcentaje', 'completado'
        ]].rename(columns={
            'id': 'ID Acción',
            'caracteristica_id': 'ID Característica',
            'categoria': 'Fase',
            'caracteristica': 'Característica',
            'descripcion': 'Acción',
            'responsable': 'Responsable',
            'recursos_count': '# Recursos',
            'recursos_total': 'Costo Recursos (USD)',
            'presupuesto': 'Presupuesto Total (USD)',
            'fecha_inicio': 'Inicio',
            'fecha_fin': 'Fin',
            'avance_porcentaje': '% Avance',
            'completado': 'Completado'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Botón para eliminar acción
    col_del, col_clear = st.columns([1, 1])
    with col_del:
        id_eliminar = st.number_input("ID de acción a eliminar", min_value=1, max_value=total_acciones, step=1)
        if st.button("🗑️ Eliminar Acción", use_container_width=True):
            st.session_state.plan_accion = [a for a in st.session_state.plan_accion if a['id'] != id_eliminar]
            st.success(f"✅ Acción {id_eliminar} eliminada")
            st.rerun()
    
    with col_clear:
        if st.button("🗑️ Limpiar Todo el Plan", use_container_width=True, type="secondary"):
            st.session_state.plan_accion = []
            st.success("✅ Plan limpiado")
            st.rerun()
    
    st.markdown("---")
    
    # ============================================================================
    # VISUALIZACIÓN DE PROGRESO HACIA VERDE
    # ============================================================================
    
    st.markdown("### 🎯 Progreso de Características hacia VERDE")
    st.caption("*Visualiza el avance de cada característica crítica hacia el cumplimiento*")
    
    # Agrupar acciones por característica
    caracteristicas_con_acciones = {}
    for accion in st.session_state.plan_accion:
        char_id = accion['caracteristica_id']
        if char_id not in caracteristicas_con_acciones:
            caracteristicas_con_acciones[char_id] = {
                'id': char_id,
                'nombre': accion['caracteristica'],
                'categoria': accion['categoria'],
                'estado_inicial': accion['estado_inicial'],
                'score_inicial': accion['score_inicial'],
                'acciones': [],
                'avance_total': 0,
                'completadas': 0,
                'total_acciones': 0
            }
        
        caracteristicas_con_acciones[char_id]['acciones'].append(accion)
        caracteristicas_con_acciones[char_id]['total_acciones'] += 1
        if accion['completado']:
            caracteristicas_con_acciones[char_id]['completadas'] += 1
        caracteristicas_con_acciones[char_id]['avance_total'] += accion['avance_porcentaje']
    
    # Calcular avance promedio por característica
    for char_id, data in caracteristicas_con_acciones.items():
        data['avance_promedio'] = data['avance_total'] / data['total_acciones'] if data['total_acciones'] > 0 else 0
        
        # Calcular estado proyectado basado en avance
        score_actual = data['score_inicial']
        avance_norm = data['avance_promedio'] / 100  # Normalizar a 0-1
        
        # Proyectar mejora: si está en rojo (0.0) y tiene 50% avance → 0.5 (amarillo)
        # Si está en amarillo (0.5) y tiene 100% avance → 1.0 (verde)
        if score_actual < 0.4:  # Rojo
            score_proyectado = score_actual + (0.5 * avance_norm)  # Puede llegar hasta 0.5 (amarillo)
        elif score_actual < 0.9:  # Amarillo
            score_proyectado = score_actual + ((1.0 - score_actual) * avance_norm)  # Puede llegar hasta 1.0 (verde)
        else:  # Verde
            score_proyectado = score_actual
        
        data['score_proyectado'] = min(score_proyectado, 1.0)
        
        # Determinar estado proyectado
        if data['score_proyectado'] >= 0.9:
            data['estado_proyectado'] = "🟢 Verde"
            data['color_proyectado'] = "#2e7d32"
        elif data['score_proyectado'] >= 0.4:
            data['estado_proyectado'] = "🟡 Amarillo"
            data['color_proyectado'] = "#f57c00"
        else:
            data['estado_proyectado'] = "🔴 Rojo"
            data['color_proyectado'] = "#c62828"
    
    # Mostrar tarjetas de progreso
    if caracteristicas_con_acciones:
        for char_id, data in caracteristicas_con_acciones.items():
            col_card, col_chart = st.columns([2, 1])
            
            with col_card:
                st.markdown(f"""
                    <div style="background: white; border-left: 4px solid {data['color_proyectado']}; 
                                padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #333; margin-bottom: 0.5rem;">
                            ID {data['id']}: {data['nombre'][:70]}...
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #666;">Estado Inicial: {data['estado_inicial']}</span>
                            <span style="color: {data['color_proyectado']}; font-weight: 600;">
                                Estado Proyectado: {data['estado_proyectado']}
                            </span>
                        </div>
                        <div style="color: #666; font-size: 0.85rem;">
                            📋 {data['completadas']}/{data['total_acciones']} acciones completadas | 
                            📊 {data['avance_promedio']:.0f}% avance promedio
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_chart:
                # Gráfico de progreso circular
                fig_progreso = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=data['avance_promedio'],
                    title={'text': "Avance", 'font': {'size': 14}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': data['color_proyectado']},
                        'steps': [
                            {'range': [0, 40], 'color': "#ffebee"},
                            {'range': [40, 80], 'color': "#fff3e0"},
                            {'range': [80, 100], 'color': "#e8f5e9"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 2},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_progreso.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_progreso, use_container_width=True, key=f"gauge_char_{char_id}")
    else:
        st.info("ℹ️ No hay acciones registradas aún")
    
    st.markdown("---")
    
    # ============================================================================
    # SECCIÓN 4: DIAGRAMA DE GANTT
    # ============================================================================
    
    st.markdown("### 📈 Diagrama de Gantt del Plan de Acción")
    
    # Botón para activar el Gantt
    if st.button("🚀 Generar Diagrama de Gantt", use_container_width=True, type="primary"):
        st.session_state.mostrar_gantt = True
    
    if st.session_state.get('mostrar_gantt', False):
        st.markdown("---")
        
        # Preparar datos para Gantt
        gantt_data = []
        for accion in st.session_state.plan_accion:
            gantt_data.append(dict(
                Task=f"{accion['id']}. {accion['caracteristica'][:30]}...",
                Start=accion['fecha_inicio'].strftime('%Y-%m-%d'),
                Finish=accion['fecha_fin'].strftime('%Y-%m-%d'),
                Resource=accion['responsable']
            ))
        
        # Crear Gantt
        if gantt_data:
            fig = ff.create_gantt(
                gantt_data,
                colors=['#1565c0', '#f57c00', '#2e7d32', '#7b1fa2', '#c62828', '#00796b'],
                index_col='Resource',
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                title='Cronograma de Acciones del Plan'
            )
            
            fig.update_layout(
                height=400 + (len(gantt_data) * 20),
                xaxis_title="Fecha",
                yaxis_title="Acciones",
                font=dict(size=10),
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="gantt_chart_plan")
            
            # Resumen por responsable
            st.markdown("#### 👥 Resumen por Responsable")
            responsables_summary = df_plan.groupby('responsable').agg({
                'id': 'count',
                'presupuesto': 'sum',
                'duracion_dias': 'mean'
            }).rename(columns={
                'id': 'Acciones Asignadas',
                'presupuesto': 'Presupuesto Total (USD)',
                'duracion_dias': 'Duración Promedio (días)'
            })
            
            st.dataframe(responsables_summary, use_container_width=True)
        else:
            st.warning("⚠️ No hay acciones para mostrar en el Gantt")

else:
    st.info("ℹ️ Agrega acciones al plan para visualizar el diagrama de Gantt")

# ============================================================================
# SECCIÓN 5: EXPORTAR PLAN
# ============================================================================

if st.session_state.plan_accion:
    st.markdown("---")
    st.markdown("### 📥 Exportar Plan de Acción")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # Exportar como Excel - preparar datos
        df_export = pd.DataFrame(st.session_state.plan_accion)
        
        # Expandir recursos para exportación
        df_export_expanded = df_export.copy()
        df_export_expanded['recursos_detalle'] = df_export_expanded['recursos'].apply(
            lambda x: '; '.join([f"{r['nombre']} ({r['tipo']}): ${r['costo']:.2f}" for r in x]) if isinstance(x, list) and x else 'Sin recursos'
        )
        df_export_expanded['recursos_total'] = df_export_expanded['recursos'].apply(
            lambda x: sum(r['costo'] for r in x) if isinstance(x, list) else 0
        )
        
        # Seleccionar columnas para exportar
        df_export_final = df_export_expanded[[
            'id', 'caracteristica_id', 'caracteristica', 'categoria', 'descripcion',
            'responsable', 'recursos_detalle', 'recursos_total', 'presupuesto',
            'fecha_inicio', 'fecha_fin', 'avance_porcentaje', 'completado'
        ]].rename(columns={
            'id': 'ID Acción',
            'caracteristica_id': 'ID Característica',
            'caracteristica': 'Característica',
            'categoria': 'Fase',
            'descripcion': 'Descripción Acción',
            'responsable': 'Responsable',
            'recursos_detalle': 'Recursos Detallados',
            'recursos_total': 'Costo Total Recursos (USD)',
            'presupuesto': 'Presupuesto Total (USD)',
            'fecha_inicio': 'Fecha Inicio',
            'fecha_fin': 'Fecha Fin',
            'avance_porcentaje': '% Avance',
            'completado': 'Completado'
        })
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja principal con el plan de acción
            df_export_final.to_excel(writer, sheet_name='Plan de Acción', index=False)
            
            # Hoja con resumen de recursos por acción
            recursos_por_accion = []
            for accion in st.session_state.plan_accion:
                if isinstance(accion['recursos'], list) and accion['recursos']:
                    for recurso in accion['recursos']:
                        recursos_por_accion.append({
                            'ID Acción': accion['id'],
                            'Característica': accion['caracteristica'],
                            'Recurso': recurso['nombre'],
                            'Tipo': recurso['tipo'],
                            'Costo (USD)': recurso['costo']
                        })
            
            if recursos_por_accion:
                df_recursos = pd.DataFrame(recursos_por_accion)
                df_recursos.to_excel(writer, sheet_name='Detalle Recursos', index=False)
            
            # Ajustar anchos de columnas en la hoja principal
            worksheet = writer.sheets['Plan de Acción']
            worksheet.column_dimensions['A'].width = 12
            worksheet.column_dimensions['B'].width = 18
            worksheet.column_dimensions['C'].width = 40
            worksheet.column_dimensions['D'].width = 20
            worksheet.column_dimensions['E'].width = 40
            worksheet.column_dimensions['F'].width = 25
            worksheet.column_dimensions['G'].width = 50
            worksheet.column_dimensions['H'].width = 20
            worksheet.column_dimensions['I'].width = 20
            worksheet.column_dimensions['J'].width = 15
            worksheet.column_dimensions['K'].width = 15
            worksheet.column_dimensions['L'].width = 12
            worksheet.column_dimensions['M'].width = 12
        
        output.seek(0)
        
        st.download_button(
            label="📊 Descargar Plan (Excel)",
            data=output,
            file_name=f"plan_accion_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_exp2:
        # Exportar resumen detallado
        total_recursos = sum(
            sum(r['costo'] for r in accion['recursos']) if isinstance(accion['recursos'], list) else 0
            for accion in st.session_state.plan_accion
        )
        
        resumen = f"""
        PLAN DE ACCIÓN - DIAGNÓSTICO
        =============================
        
        Total de Acciones: {len(st.session_state.plan_accion)}
        Acciones Completadas: {acciones_completadas}
        Presupuesto Total: ${presupuesto_total:,.2f}
        Costo Total Recursos: ${total_recursos:,.2f}
        Duración Promedio: {duracion_promedio:.0f} días
        
        Características Atendidas: {len(set([a['caracteristica'] for a in st.session_state.plan_accion]))}
        
        DETALLE DE RECURSOS
        ===================
        """
        
        for accion in st.session_state.plan_accion:
            resumen += f"\n\nAcción {accion['id']}: {accion['caracteristica'][:50]}..."
            if isinstance(accion['recursos'], list) and accion['recursos']:
                resumen += f"\nRecursos ({len(accion['recursos'])}):"
                for recurso in accion['recursos']:
                    resumen += f"\n  • {recurso['nombre']} ({recurso['tipo']}) - ${recurso['costo']:,.2f}"
            else:
                resumen += "\n  Sin recursos especificados"
        
        st.download_button(
            label="📄 Descargar Resumen (TXT)",
            data=resumen,
            file_name=f"resumen_plan_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
