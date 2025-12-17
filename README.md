# 🚀 Sistema de Gestión de Evaluación de Innovación

Sistema modular para evaluar proyectos de innovación usando metodologías IRL (Innovation Readiness Level) y EBCT (34 Características Organizacionales).

## 📋 Características Principales

### ✨ Flujo Modular
- **Fase 0**: Gestión de portafolio de proyectos
- **Fase 1**: Evaluación IRL (6 dimensiones, 151 preguntas)
- **Fase 2**: Evaluación EBCT (34 características, 4 fases)
- **Fase 3**: Diagnóstico (evaluación integrada de capacidades)
- **Fase 4**: Indicadores (dashboards y reportes)

### 🔄 Modos de Trabajo
1. **Sesión Única**: Evalúa todo en una sesión, sin archivos intermedios
2. **Archivos Modulares**: Exporta/importa por fase, trabajo distribuido
3. **Consolidación**: Combina evaluaciones de diferentes fuentes

### 📥📤 Sistema de Carga/Descarga
- Descarga plantillas vacías para empezar
- Exporta datos actuales en cualquier momento
- Anexa nuevos proyectos sin borrar existentes
- Consolida archivos separados en uno solo

## 🎯 Inicio Rápido

### Opción A: Desde Cero
```
1. Fase 0 → Descargar plantilla → Llenar proyectos → Cargar
2. Fase 1 → Seleccionar proyecto → Evaluar IRL
3. Fase 2 → Seleccionar proyecto → Evaluar EBCT
4. Fase 3 → Visualizar diagnóstico integrado
5. Fase 4 → Visualizar indicadores y dashboards
```

### Opción B: Con Archivos Separados
```
1. Descargar plantilla de Fase 0 → Llenar → Exportar
2. Descargar plantilla de Fase 1 → Evaluar → Exportar
3. Descargar plantilla de Fase 2 → Evaluar → Exportar
4. Fase 3 → Visualizar análisis integrado
5. Fase 4 → Cargar datos → Visualizar indicadores
```

## 📂 Estructura de Archivos

### Archivos de Entrada
- `plantilla_portafolio.xlsx` - Plantilla vacía de portafolio
- `Evaluacion_IRL_Proyecto_X.xlsx` - Plantilla de evaluación IRL
- `instructivo_portafolio.xlsx` - Guía de uso

### Archivos de Salida
- `portafolio_actual_YYYYMMDD_HHMM.xlsx` - Portafolio exportado
- `evaluacion_IRL_*.xlsx` - Evaluaciones IRL completadas
- `evaluacion_EBCT_*.xlsx` - Evaluaciones EBCT completadas
- `CONSOLIDADO_YYYYMMDD_HHMMSS.xlsx` - Archivo consolidado único

## 🔗 Páginas del Sistema

### 1. 📂 Fase 0 - Portafolio
**Propósito**: Gestionar catálogo de proyectos

**Funcionalidades**:
- 📥 Descargar plantilla vacía
- 📖 Descargar instructivo
- 📤 Exportar datos actuales
- ⬆️ Cargar proyectos (Reemplazar/Anexar)
- 🟢 Indicador de estado (X proyectos cargados)
- 📅 Timestamp de última carga

**Flujo**:
```
Descargar plantilla → Llenar Excel → Cargar → Verificar estado
```

### 2. 📈 Fase 1 - IRL
**Propósito**: Evaluar madurez tecnológica

**Funcionalidades**:
- Evaluación de 6 dimensiones × 9 niveles
- 151 preguntas VERDADERO/FALSO
- Descarga de plantilla pre-llenada (todas en FALSO)
- Carga masiva desde Excel
- Panel de resultados por dimensión

**Dimensiones Evaluadas**:
1. Investigación y Validación Técnica
2. Estrategia de Propiedad Intelectual
3. Preparación del Mercado
4. Preparación Organizacional
5. Evaluación de Riesgos y Financiamiento
6. Estrategia y Gestión para Exportación

### 3. 🧭 Fase 2 - EBCT
**Propósito**: Evaluar capacidades organizacionales

**Funcionalidades**:
- 34 características en 4 fases
- Estados: 🟢 Verde, 🟡 Amarillo, 🔴 Rojo
- Plan de acción con fechas
- Semáforo de innovación visual
- Radar de cumplimiento por fase

**Fases EBCT**:
1. Fase Incipiente (Características 1-9)
2. Fase Validación y PI (Características 10-17)
3. Fase Preparación para Mercado (Características 18-29)
4. Fase Internacionalización (Características 30-34)

### 4. 🎯 Fase 3 - Diagnóstico
**Propósito**: Evaluación integrada de capacidades

**Funcionalidades**:
- Integración de resultados IRL y EBCT
- Identificación de factores críticos
- Análisis de brechas
- Recomendaciones estratégicas

### 5. 📈 Fase 4 - Indicadores
**Propósito**: Visualización y análisis de desempeño

**Tabs**:
- **Generales**: Métricas globales, distribución, rankings
- **Comparativo**: Comparar 2+ proyectos (radares, semáforos)
- **Individual**: Vista detallada por proyecto

**Gráficos**:
- Radar IRL (6 dimensiones)
- Radar EBCT (4 fases, % cumplimiento)
- Pie EBCT (distribución Verde/Amarillo/Rojo)
- Semáforo de innovación (matriz 4×34)
- Tablas con degradados y filtros

## 📊 Indicadores Clave

### IRL (Innovation Readiness Level)
- **Escala**: 1-9 por dimensión
- **No se promedian**: Cada dimensión es independiente
- **IRL Rango**: Mínimo-Máximo alcanzado
- **IRL Media**: Promedio de referencia

### EBCT (Características Organizacionales)
- **Cumplimiento**: % características en verde
- **Distribución**: Verdes/Amarillas/Rojas
- **Por Fase**: Cumplimiento % en cada fase (1-4)

### Madurez Global
```
Madurez = (IRL_promedio/9 × 40%) + (EBCT_cumplimiento × 60%)
```
- 40% peso tecnología (IRL)
- 60% peso organización (EBCT)
- Resultado: 0-100%

## 🎨 Indicadores Visuales

### Estados de Carga
- 🟢 **Tiene datos** - Sistema cargado correctamente
- ⚪ **Sin datos** - Descarga plantilla para empezar
- 📅 **Timestamp** - Fecha y hora de última carga

### Estados EBCT
- 🟢 **Verde** - Cumple satisfactoriamente
- 🟡 **Amarillo** - En desarrollo/progreso
- 🔴 **Rojo** - No cumple, requiere acción

## 💡 Tips de Uso

### Para Gestores de Proyecto
✅ Trabaja fase por fase, no todo de una vez  
✅ Usa la plantilla Excel de IRL (ahorra 80% del tiempo)  
✅ Descarga respaldos antes de cambios masivos  
✅ Revisa el indicador de estado antes de avanzar  

### Para Evaluadores
✅ Sé realista con los estados (amarillo es válido)  
✅ Agrega evidencias detalladas  
✅ Define fechas realistas en plan de acción  
✅ Usa el modo "Anexar" para agregar sin borrar  

### Para Equipos Distribuidos
✅ Cada persona trabaja su fase y exporta  
✅ El consolidador une todo sin conflictos  
✅ Nombra archivos con fecha: `portafolio_2024_11_20.xlsx`  
✅ Valida IDs antes de consolidar  

## 🔧 Requisitos Técnicos

### Python Packages
```python
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
openpyxl>=3.1.0  # Requerido para Excel
```

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
streamlit run app.py
```

## 📖 Documentación

- **Manual de Usuario**: Ver `MANUAL_USUARIO.md`
- **Ayuda Contextual**: Tooltips (ⓘ) en cada página
- **Expanders de Ayuda**: "❓ Cómo usar esta página"

## 🚨 Solución de Problemas

### Problema: "No se muestran proyectos"
**Solución**: Verifica el indicador de estado en Fase 0. Debe mostrar "🟢 X proyectos cargados"

### Problema: "Error al cargar Excel"
**Solución**: Instala openpyxl: `pip install openpyxl`

### Problema: "IDs inconsistentes"
**Solución**: Los IDs deben ser EXACTAMENTE iguales en los 3 archivos (case-sensitive)

### Problema: "VERDADERO/FALSO → TRUE/FALSE"
**Solución**: Descarga la nueva plantilla con formato de texto. El sistema normaliza automáticamente.

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Revisa el `MANUAL_USUARIO.md`
2. Verifica la ayuda contextual en la aplicación
3. Contacta al administrador del sistema

---

**Versión**: 2.0  
**Fecha**: Noviembre 2024  
**Licencia**: Uso Interno  
**Desarrollado por**: Grupo DeiDanilo