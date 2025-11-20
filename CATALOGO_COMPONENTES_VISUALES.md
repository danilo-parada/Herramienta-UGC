# 🎨 Catálogo de Componentes Visuales Interactivos

## 📚 Componentes Disponibles

Sistema modular de instructivos visuales con CSS moderno y animaciones para mejorar la experiencia del usuario.

---

## 1. 🔀 Mode Selector Guide

**Función**: `render_mode_selector_guide(current_mode: str)`

### Descripción
Guía visual interactiva para selector de modo con tarjetas animadas que explican las diferencias entre modo Conectado e Individual.

### Características
- ✨ Gradiente animado de fondo con efecto pulse
- 🎴 Tarjetas con hover effect (elevación y sombra)
- ✅ Indicador visual del modo activo
- 📱 Diseño responsive (grid adaptable)
- 🎯 Lista de features con checks verdes

### Uso
```python
from core.instructivos import render_mode_selector_guide

current_mode = st.session_state.get('irl_mode', 'conectado')
st.markdown(render_mode_selector_guide(current_mode), unsafe_allow_html=True)
```

### Preview Visual
```
┌────────────────────────────────────────────────┐
│ 🔀 Selecciona tu Modo de Trabajo              │
├────────────────────┬───────────────────────────┤
│ 🔗 Modo Conectado  │ 🔓 Modo Individual       │
│ [✓ ACTIVO]         │                          │
│                    │                          │
│ ✓ Usa datos Fase 0 │ ✓ Todos los proyectos   │
│ ✓ Solo priorizados │ ✓ Sin depender ranking  │
│ ✓ Validación auto  │ ✓ Carga directa         │
│ ✓ Navegación fluida│ ✓ Máxima flexibilidad   │
└────────────────────┴───────────────────────────┘
```

---

## 2. 📋 Stepper Guide

**Función**: `render_stepper_guide(steps: List[Dict], current_step: int)`

### Descripción
Guía paso a paso vertical con números/iconos, indicadores de progreso y línea conectora animada.

### Características
- 🔢 Números circulares con gradientes según estado
- 📍 Línea conectora vertical entre pasos
- ✅ Estados: completed (verde), active (azul), pending (gris)
- 💫 Animación pulse en paso activo
- 🎨 Bordes laterales de color según estado

### Uso
```python
from core.instructivos import render_stepper_guide

steps = [
    {"icon": "📥", "title": "Descargar", "description": "Obtén la plantilla"},
    {"icon": "📝", "title": "Completar", "description": "Llena tus datos"},
    {"icon": "📤", "title": "Subir", "description": "Carga el archivo"},
    {"icon": "✅", "title": "Confirmar", "description": "Valida y aplica"}
]

st.markdown(render_stepper_guide(steps, current_step=1), unsafe_allow_html=True)
```

### Preview Visual
```
┌─────────────────────────────────────┐
│ 📋 Guía Paso a Paso                 │
├─────────────────────────────────────┤
│ ┌───┐                               │
│ │ ✓ │ Descargar              [✓]   │
│ └─│─┘ Obtén la plantilla            │
│   │                                 │
│ ┌─▼─┐                               │
│ │ 2 │ Completar              [⏵]   │
│ └─│─┘ Llena tus datos               │
│   │                                 │
│ ┌─▼─┐                               │
│ │ 3 │ Subir                  [○]   │
│ └─│─┘ Carga el archivo              │
│   │                                 │
│ ┌─▼─┐                               │
│ │ 4 │ Confirmar              [○]   │
│ └───┘ Valida y aplica               │
└─────────────────────────────────────┘
```

---

## 3. 🎴 Action Card

**Función**: `render_action_card(title, description, icon, actions, color)`

### Descripción
Tarjeta de acción con ícono grande, descripción y botones estilizados.

### Características
- 🎨 4 esquemas de color: blue, green, purple, orange
- 📦 Ícono grande con fondo de color suave
- 🔘 Botones primary y secondary
- 💡 Textos de ayuda bajo cada botón
- 🎭 Hover effect con elevación

### Uso
```python
from core.instructivos import render_action_card

st.markdown(render_action_card(
    title="Descarga tu Plantilla",
    description="Excel optimizado con todas las columnas necesarias",
    icon="📥",
    actions=[
        {
            "label": "⬇️ Descargar Excel",
            "type": "primary",
            "help": "Archivo: plantilla_portafolio.xlsx"
        },
        {
            "label": "📖 Ver Instructivo",
            "type": "secondary",
            "help": "Guía paso a paso"
        }
    ],
    color="blue"
), unsafe_allow_html=True)
```

### Preview Visual
```
┌─────────────────────────────────────┐
│ ┌────┐                              │
│ │ 📥 │  Descarga tu Plantilla       │
│ └────┘  Excel optimizado...         │
│                                     │
│ [⬇️ Descargar Excel] [📖 Instructivo]│
│  plantilla.xlsx      paso a paso    │
└─────────────────────────────────────┘
```

---

## 4. 🔄 Flow Diagram

**Función**: `render_flow_diagram(flow_type: str)`

### Descripción
Diagrama de flujo animado mostrando el proceso según el modo (conectado/individual).

### Características
- 🌊 Efecto shimmer animado en fondo
- 🎯 Círculos flotantes con bounce animation
- ➡️ Flechas conectoras automáticas
- 📱 Layout responsive (vertical en mobile)
- 🎨 2 estilos: gradiente morado (conectado) o rosa (individual)

### Uso
```python
from core.instructivos import render_flow_diagram

# Modo conectado
st.markdown(render_flow_diagram("conectado"), unsafe_allow_html=True)

# Modo individual
st.markdown(render_flow_diagram("individual"), unsafe_allow_html=True)
```

### Preview Visual - Conectado
```
┌──────────────────────────────────────────┐
│ 🔗 Flujo Modo Conectado                  │
│                                          │
│  📂  ──▶  📈  ──▶  🧭  ──▶  📊          │
│ Port.    IRL     EBCT   Indicad.        │
└──────────────────────────────────────────┘
```

### Preview Visual - Individual
```
┌──────────────────────────────────────────┐
│ 🔓 Flujo Modo Individual                 │
│                                          │
│ ┌─────────┬─────────┐                   │
│ │📥 Desc. │📝 Complet│                   │
│ ├─────────┼─────────┤                   │
│ │📤 Sube  │🔗 Consol.│                   │
│ └─────────┴─────────┘                   │
└──────────────────────────────────────────┘
```

---

## 5. 💡 Quick Tips

**Función**: `render_quick_tips(tips: List[str], color: str)`

### Descripción
Panel de tips rápidos con estilo visual destacado y emojis.

### Características
- 🎨 4 colores disponibles: blue, green, orange, purple
- 💡 Emoji de bombilla en cada tip
- 📦 Fondo degradado suave
- 📏 Borde lateral de color

### Uso
```python
from core.instructivos import render_quick_tips

tips = [
    "Descarga la plantilla antes de empezar",
    "Guarda respaldos regularmente",
    "Lee el instructivo completo",
    "Valida los IDs antes de consolidar"
]

st.markdown(render_quick_tips(tips, "green"), unsafe_allow_html=True)
```

### Preview Visual
```
┌─────────────────────────────────────┐
│ ⚡ Tips Rápidos                      │
├─────────────────────────────────────┤
│ 💡 Descarga la plantilla primero    │
│ 💡 Guarda respaldos regularmente    │
│ 💡 Lee el instructivo completo      │
│ 💡 Valida IDs antes de consolidar   │
└─────────────────────────────────────┘
```

---

## 6. 🔍 Tooltip Help (Bonus)

**Función**: `render_tooltip_help(text: str, tooltip: str)`

### Descripción
Texto con tooltip interactivo al pasar el mouse.

### Características
- 🎯 Aparece al hover
- 🎨 Fondo oscuro con texto blanco
- 📍 Flecha apuntando al texto
- ✨ Animación suave de aparición

### Uso
```python
from core.instructivos import render_tooltip_help

html = render_tooltip_help(
    text="modo conectado",
    tooltip="Usa datos de la sesión actual sin cargar archivos"
)
st.markdown(f"Selecciona el {html} para continuar", unsafe_allow_html=True)
```

---

## 🎨 Paleta de Colores

### Blue (Default)
- Primary: `#2196F3`
- Light: `#e3f2fd`
- Dark: `#1976D2`
- **Uso**: Acciones principales, información

### Green
- Primary: `#4CAF50`
- Light: `#e8f5e9`
- Dark: `#388E3C`
- **Uso**: Éxito, confirmación, completado

### Purple
- Primary: `#9C27B0`
- Light: `#f3e5f5`
- Dark: `#7B1FA2`
- **Uso**: Tips, ayuda, modo individual

### Orange
- Primary: `#FF9800`
- Light: `#fff3e0`
- Dark: `#F57C00`
- **Uso**: Advertencias, atención

---

## 📱 Responsive Design

Todos los componentes incluyen media queries para adaptarse a pantallas pequeñas:

```css
@media (max-width: 768px) {
    /* Grid de 2 columnas → 1 columna */
    /* Flujo horizontal → vertical */
    /* Tamaños de fuente ajustados */
}
```

---

## 🎭 Animaciones Disponibles

### Pulse
```css
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}
```

### Bounce
```css
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
```

### Shimmer
```css
@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}
```

---

## 🚀 Integración en Páginas

### Página de Portafolio
```python
# En pages/02_📂_Fase_0_Portafolio.py
from core.instructivos import render_stepper_guide, render_quick_tips

steps = [...]
st.markdown(render_stepper_guide(steps, 0), unsafe_allow_html=True)

tips = [...]
st.markdown(render_quick_tips(tips, "blue"), unsafe_allow_html=True)
```

### Página IRL
```python
# En pages/03_📈_Fase_1_IRL.py
from core.instructivos import (
    render_mode_selector_guide,
    render_flow_diagram,
    render_action_card
)

# Selector de modo
st.markdown(render_mode_selector_guide(current_mode), unsafe_allow_html=True)

# Flujo visual
st.markdown(render_flow_diagram(mode), unsafe_allow_html=True)

# Tarjeta de descarga
st.markdown(render_action_card(...), unsafe_allow_html=True)
```

### Página EBCT
```python
# En pages/04_🧭_Fase_2_EBCT.py
from core.instructivos import render_stepper_guide, render_quick_tips

# Similar a IRL, adaptando los pasos
```

---

## 💡 Best Practices

### ✅ Hacer
- Usar `unsafe_allow_html=True` para renderizar
- Combinar múltiples componentes para guías completas
- Mantener colores consistentes por tipo de acción
- Agregar textos de ayuda (`help`) en action cards

### ❌ Evitar
- No mezclar demasiados colores en la misma página
- No abusar de animaciones (pueden distraer)
- No olvidar el try/except al importar (fallback)
- No hardcodear colores, usar esquemas predefinidos

---

## 🔧 Mantenimiento

### Agregar Nuevo Componente
1. Crear función en `core/instructivos.py`
2. Definir HTML + CSS con animaciones
3. Parametrizar colores y contenido
4. Documentar en este catálogo
5. Agregar ejemplos de uso

### Modificar Estilos
- Todos los estilos están embebidos en cada función
- Cambiar valores en `color_schemes` o `color_map`
- Mantener consistencia con tema existente

---

## 📊 Métricas de UX

### Antes (Sin Instructivos)
- ❌ Usuarios confundidos sobre qué hacer
- ❌ Pasos no claros
- ❌ Modo conectado/individual no explicado
- ❌ Ayuda solo en tooltips estándar

### Después (Con Instructivos)
- ✅ Guía visual paso a paso
- ✅ Tarjetas explicativas interactivas
- ✅ Diagramas de flujo animados
- ✅ Tips contextuales destacados
- ✅ Feedback visual del estado actual

---

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Autor**: Sistema de Gestión UGC  
**Módulo**: `core/instructivos.py`
