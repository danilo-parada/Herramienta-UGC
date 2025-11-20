# 🔀 Arquitectura Dual Mode - Flujo Flexible

## 📋 Concepto General

El sistema ahora soporta **2 modos de trabajo** en cada fase, dándole al usuario **flexibilidad total** para elegir cómo trabajar:

### **🔗 Modo Conectado** (Flujo Integrado)
- Trabaja con datos cargados en `st.session_state` de fases anteriores
- Validación automática de dependencias
- Flujo continuo: Portafolio → IRL → EBCT → Indicadores
- **Ideal para**: Evaluación completa en una sesión

### **🔓 Modo Individual** (Flujo Independiente)
- Cada fase funciona de manera autónoma
- Carga archivos específicos sin depender de otras fases
- Acceso a todos los proyectos del portafolio maestro
- **Ideal para**: Trabajo distribuido, actualización de una sola fase

---

## 🎯 Implementación por Página

### ✅ **Fase 0: Portafolio** (Base del Sistema)
**Estado**: ✅ Completo

**Características**:
- Siempre en modo "base" - no tiene dependencias
- Carga proyectos desde Excel (anexar/reemplazar)
- Exporta datos actuales con timestamp
- Status badges: 🟢 X proyectos cargados

**Funcionalidad**:
```python
# Descarga plantilla vacía → Llena → Carga
# Opción: Anexar nuevos sin borrar existentes
# Exporta: portafolio_actual_YYYYMMDD_HHMM.xlsx
```

---

### ✅ **Fase 1: IRL** (Dual Mode Implementado)
**Estado**: ✅ Modo Dual Implementado

**Selector Visual**:
```
┌─────────────────────────────────────────┐
│ 🔀 Modo de Trabajo                      │
├─────────────────────────────────────────┤
│ ⚪ 🔗 Modo Conectado                     │
│ ⚪ 🔓 Modo Individual                    │
└─────────────────────────────────────────┘
```

#### **🔗 Modo Conectado**
**Requiere**:
- Payload de Fase 0 (`fase1_payload` en session_state)
- Ranking calculado

**Muestra**:
- Solo proyectos del ranking priorizados
- Botón "Ir a Fase 0" si no hay datos

**Status Badge**:
```
✅ Modo Conectado Activo
🟢 5 proyecto(s) disponible(s) desde Fase 0
```

#### **🔓 Modo Individual**
**Requiere**:
- Solo portafolio maestro con proyectos

**Muestra**:
- Todos los proyectos del portafolio
- No requiere ranking

**Status Badge**:
```
📂 Modo Individual Activo

En este modo puedes:
- 📥 Descargar plantilla IRL vacía
- 📝 Completar evaluación offline
- 📤 Cargar archivo IRL directamente
- ✅ Trabajar sin depender de otras fases
```

**Lógica Implementada**:
```python
if st.session_state.irl_mode == 'conectado':
    # Valida payload de Fase 0
    # Filtra proyectos por ranking
    # Muestra solo priorizados
else:
    # Obtiene todos los proyectos del portafolio
    # No requiere ranking
    # Trabajo independiente
```

---

### 🔄 **Fase 2: EBCT** (Por Implementar)
**Estado**: ⏳ Pendiente

**Plan de Implementación**:

#### **🔗 Modo Conectado**
**Requiere**:
- Portafolio cargado (obligatorio)
- IRL evaluado (opcional pero recomendado)

**Funcionalidad**:
- Continúa evaluación desde IRL
- Botón "Ir a Fase 1" para completar IRL primero
- Hereda contexto del proyecto

**Status Badge**:
```
✅ Modo Conectado Activo
🟢 Portafolio: 10 proyectos
🟢 IRL: 5 evaluados
```

#### **🔓 Modo Individual**
**Requiere**:
- Solo portafolio maestro

**Funcionalidad**:
- Descarga plantilla EBCT vacía
- Completa offline
- Carga archivo EBCT directamente
- Trabaja sin IRL previo

**Status Badge**:
```
📂 Modo Individual Activo

Puedes evaluar EBCT sin haber completado IRL.
Descarga la plantilla y completa offline.
```

---

### 📊 **Indicadores** (Por Implementar)
**Estado**: ⏳ Pendiente

**Plan de 3 Modos**:

#### **Opción 1: 🔗 Desde Sesión Actual**
```python
# Lee de st.session_state
portafolio_df = st.session_state.portafolio
irl_resultados = st.session_state.irl_resultados
ebct_evaluaciones = st.session_state.ebct_evaluaciones
```

**Ventaja**: Flujo continuo, sin archivos intermedios

#### **Opción 2: 📂 Cargar Consolidado Único**
```python
# Carga archivo consolidado generado previamente
consolidado = pd.read_excel(uploaded_file, sheet_name=None)
# Sheets: Indice, IRL, EBCT, Acciones
```

**Ventaja**: Un solo archivo, fácil de compartir

#### **Opción 3: 🔗 Consolidar Archivos Separados**
```python
# Usa página 07 - Consolidador
# Sube 3 archivos: Portafolio + IRL + EBCT
# Genera consolidado automáticamente
```

**Ventaja**: Trabajo distribuido, máxima flexibilidad

---

## 🎨 Componentes UI Reutilizables

### Status Badge Component
```python
def render_status_badge(mode: str, data_available: bool, count: int = 0):
    if mode == 'conectado':
        if data_available:
            st.success(f"✅ Modo Conectado Activo\n\n🟢 {count} proyecto(s) disponible(s)")
        else:
            st.warning("⚠️ Sin datos de fase anterior")
    else:
        st.info("""
        📂 Modo Individual Activo
        - Trabaja sin dependencias
        - Carga archivos directamente
        """)
```

### Mode Selector Component
```python
def render_mode_selector(page_name: str):
    mode = st.radio(
        "Selecciona cómo quieres trabajar:",
        options=["🔗 Modo Conectado", "🔓 Modo Individual"],
        help="Conectado: usa datos de sesión | Individual: carga archivos directamente"
    )
    return "conectado" if "🔗" in mode else "individual"
```

---

## 📊 Casos de Uso

### **Caso 1: Evaluación Completa (Modo Conectado)**
```
Usuario Tipo: Evaluador individual, sesión única
Flujo:
1. Fase 0 → Carga portafolio completo
2. Fase 0 → Calcula ranking
3. Fase 1 (Conectado) → Evalúa IRL de proyectos priorizados
4. Fase 2 (Conectado) → Evalúa EBCT continuando desde IRL
5. Indicadores (Sesión) → Visualiza todo sin cargar archivos
```

**Ventajas**:
- ✅ Flujo rápido sin interrupciones
- ✅ Validación automática de dependencias
- ✅ Datos siempre consistentes

---

### **Caso 2: Trabajo Distribuido (Modo Individual)**
```
Escenario: 3 evaluadores, cada uno trabaja una fase

Evaluador A (Portafolio):
1. Fase 0 → Carga proyectos
2. Fase 0 → Exporta: portafolio_actual_20241120.xlsx
3. Envía archivo a B y C

Evaluador B (IRL):
1. Fase 1 (Individual) → Descarga plantilla IRL
2. Completa offline (151 preguntas)
3. Carga en plataforma o exporta: evaluacion_IRL_20241120.xlsx

Evaluador C (EBCT):
1. Fase 2 (Individual) → Descarga plantilla EBCT
2. Completa offline (34 características)
3. Exporta: evaluacion_EBCT_20241120.xlsx

Coordinador (Consolidación):
1. Página 07 → Sube 3 archivos
2. Valida IDs
3. Genera consolidado
4. Indicadores → Carga consolidado y visualiza
```

**Ventajas**:
- ✅ Paralelización del trabajo
- ✅ Especialización por fase
- ✅ Sin conflictos de sesión

---

### **Caso 3: Actualización Parcial (Modo Mixto)**
```
Escenario: Sistema en producción, actualizar solo IRL de 1 proyecto

1. Fase 0 (Ya tiene datos) → Sin cambios
2. Fase 1 (Individual) → Cambia a modo individual
3. Selecciona proyecto específico
4. Re-evalúa IRL
5. Exporta solo ese IRL actualizado
6. Consolidador → Mezcla IRL nuevo con EBCT existente
```

**Ventajas**:
- ✅ No afecta otros proyectos
- ✅ Actualización quirúrgica
- ✅ Auditoría por timestamps

---

## 🔧 Implementación Técnica

### Session State Structure
```python
# Portafolio (Base)
st.session_state.portafolio = pd.DataFrame()  # Siempre disponible
st.session_state.portafolio_loaded_at = datetime(...)

# IRL (Dual Mode)
st.session_state.irl_mode = 'conectado' | 'individual'
st.session_state.irl_resultados = pd.DataFrame()
st.session_state.fase1_payload = {...}  # Solo en conectado
st.session_state.fase1_ready = bool

# EBCT (Dual Mode - pendiente)
st.session_state.ebct_mode = 'conectado' | 'individual'
st.session_state.ebct_evaluacion = pd.DataFrame()
st.session_state.fase2_payload = {...}  # Solo en conectado

# Indicadores (Triple Mode - pendiente)
st.session_state.indicadores_source = 'sesion' | 'consolidado' | 'separados'
```

### Validation Logic
```python
def validate_dependencies(mode: str, phase: str) -> bool:
    if mode == 'individual':
        # Solo requiere portafolio maestro
        return len(db.fetch_df()) > 0
    
    # Modo conectado: valida fase anterior
    if phase == 'irl':
        return st.session_state.get('fase1_ready', False)
    elif phase == 'ebct':
        return len(st.session_state.get('portafolio', [])) > 0
    elif phase == 'indicadores':
        # Al menos una evaluación disponible
        return (len(st.session_state.get('irl_resultados', [])) > 0 or
                len(st.session_state.get('ebct_evaluacion', [])) > 0)
```

---

## 📈 Beneficios del Sistema Dual

### Para Evaluadores Individuales
✅ **Conectado**: Flujo rápido sin interrupciones  
✅ **Individual**: Flexibilidad para volver a fases específicas  

### Para Equipos Distribuidos
✅ **Paralelización**: Varias personas trabajan simultáneamente  
✅ **Sin conflictos**: Archivos separados, consolidación posterior  

### Para Administradores
✅ **Auditoría**: Timestamps en cada archivo  
✅ **Versiones**: Archivos con fecha, historial claro  
✅ **Backup**: Exportaciones regulares automáticas  

### Para el Sistema
✅ **Robustez**: Menos dependencias = menos errores  
✅ **Escalabilidad**: Fácil agregar nuevas fases  
✅ **Mantenibilidad**: Lógica clara y separada  

---

## 🚀 Roadmap de Implementación

### ✅ **Fase 1: COMPLETADO**
- [x] Portafolio con exportación
- [x] Status badges
- [x] IRL modo dual implementado
- [x] Consolidador página 07

### 🔄 **Fase 2: EN PROGRESO**
- [x] Documentación arquitectura
- [ ] EBCT modo dual
- [ ] Exportación IRL actual
- [ ] Exportación EBCT actual

### ⏳ **Fase 3: PENDIENTE**
- [ ] Indicadores triple mode
- [ ] Status badges en EBCT/Indicadores
- [ ] Manual actualizado con ambos flujos
- [ ] Testing end-to-end

---

## 💡 Tips de Implementación

### Para Desarrolladores
```python
# Patrón para agregar modo dual a cualquier página:

# 1. Selector de modo
mode = render_mode_selector("nombre_fase")

# 2. Lógica condicional
if mode == 'conectado':
    # Valida dependencies
    # Filtra datos según payload
else:
    # Obtiene todos los datos disponibles
    # Trabajo independiente

# 3. Status badge
render_status_badge(mode, data_available, count)
```

### Para UX
- Modo por defecto: **Conectado** (flujo natural)
- Cambiar a Individual: explícito con radio button
- Ayuda contextual en cada modo
- Status siempre visible

---

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Autor**: Sistema de Gestión UGC
