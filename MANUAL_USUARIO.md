# 📖 Manual de Usuario - Sistema de Gestión de Innovación

## 🎯 Descripción General

Este sistema permite evaluar y gestionar proyectos de innovación a través de 3 fases principales:
- **Fase 0**: Portafolio y filtro inicial
- **Fase 1**: Evaluación IRL (Innovation Readiness Level)
- **Fase 2**: Evaluación EBCT (34 Características Organizacionales)
- **Consolidador**: Combinar evaluaciones separadas
- **Indicadores**: Visualización y seguimiento

---

## 🚀 Guía de Inicio Rápido

### Escenario 1: Empezar desde Cero

#### Paso 1: Crear Portafolio de Proyectos
1. Ve a **📂 Fase 0 - Portafolio**
2. Haz clic en **"📥 Descargar plantilla vacía"**
3. Abre el archivo Excel descargado
4. Llena los datos de tus proyectos:
   - ID_Proyecto (único por proyecto)
   - Nombre_Proyecto
   - Responsable
   - Estado (Activo, En pausa, Cancelado, etc.)
   - Presupuesto_Total
   - Otros campos según necesidades
5. Guarda el archivo
6. En la aplicación, haz clic en **"Cargar portafolio (CSV o Excel)"**
7. Selecciona **"Reemplazar portafolio actual"**
8. Haz clic en **"Aplicar carga del archivo"**

✅ **Resultado**: Verás el indicador "🟢 X proyectos cargados"

#### Paso 2: Evaluar Madurez Tecnológica (IRL)
1. Ve a **📈 Fase 1 - IRL**
2. Selecciona un proyecto del dropdown
3. **Opción A - Evaluación Manual**:
   - Responde las 151 preguntas marcando VERDADERO/FALSO
   - Agrega evidencias cuando sea VERDADERO
   - Haz clic en **"Guardar Respuestas"**

4. **Opción B - Evaluación por Excel** (RECOMENDADO):
   - Haz clic en **"⬇️ Descargar Plantilla Excel"**
   - Abre el archivo (todas las respuestas vienen pre-llenadas con FALSO)
   - Cambia a VERDADERO solo las que SÍ cumplan
   - Agrega evidencia en la columna correspondiente
   - Guarda y sube el archivo
   - Revisa la tabla de confirmación
   - Haz clic en **"Confirmar y Evaluar"**

✅ **Resultado**: Verás el panel de resultados con las 6 dimensiones evaluadas

#### Paso 3: Evaluar Características Organizacionales (EBCT)
1. Ve a **🧭 Fase 2 - EBCT**
2. Selecciona el mismo proyecto
3. Evalúa las 34 características (organiza por fase 1-4)
4. Para cada característica, marca el estado:
   - 🟢 Verde: Cumple satisfactoriamente
   - 🟡 Amarillo: En desarrollo
   - 🔴 Rojo: No cumple - Requiere acción
5. Haz clic en **"Guardar Evaluación"**

✅ **Resultado**: Verás el panel con semáforo de innovación y resultados

#### Paso 4: Consolidar y Visualizar
1. **Si trabajaste en la misma sesión**: Ve directo a **📊 Indicadores y Seguimiento**

2. **Si trabajaste en sesiones separadas**:
   - Ve a **📂 Fase 0** → Haz clic en **"📤 Descargar datos actuales"**
   - Ve a **📈 Fase 1** → Descarga el archivo de evaluación
   - Ve a **🧭 Fase 2** → Descarga el archivo de evaluación EBCT
   - Ve a **🔗 Consolidador**
   - Sube los 3 archivos
   - Haz clic en **"🚀 Generar Consolidado"**
   - Descarga el archivo CONSOLIDADO
   - Ve a **📊 Indicadores y Seguimiento** → Carga el archivo consolidado

✅ **Resultado**: Verás todos los indicadores, gráficos comparativos y reportes

---

### Escenario 2: Actualizar Evaluación Existente

#### Caso: Ya tienes proyectos evaluados y quieres agregar más

1. **Agregar nuevos proyectos al portafolio**:
   - Ve a **📂 Fase 0 - Portafolio**
   - Haz clic en **"📤 Descargar datos actuales"** (guárdalo como respaldo)
   - Descarga la **"📥 plantilla vacía"**
   - Llena SOLO los nuevos proyectos
   - Sube el archivo
   - Selecciona **"Anexar al portafolio actual"** ⚠️ IMPORTANTE
   - Haz clic en **"Aplicar carga del archivo"**

✅ **Resultado**: Los nuevos proyectos se agregan sin borrar los existentes

2. **Evaluar los nuevos proyectos**:
   - Repite el Paso 2 y 3 del Escenario 1 para cada nuevo proyecto

3. **Modificar evaluación existente**:
   - Ve a la fase correspondiente (IRL o EBCT)
   - Selecciona el proyecto
   - Modifica las respuestas/estados necesarios
   - Guarda nuevamente

✅ **Resultado**: Las evaluaciones se actualizan automáticamente

---

### Escenario 3: Trabajo Colaborativo (Archivos Separados)

#### Situación: Diferentes personas trabajan en diferentes fases

**Persona A - Gestiona Portafolio**:
1. Carga/actualiza proyectos en Fase 0
2. Descarga **"📤 Descargar datos actuales"**
3. Comparte archivo `portafolio_actual_YYYYMMDD_HHMM.xlsx`

**Persona B - Evalúa IRL**:
1. Recibe archivo de portafolio
2. (Opcional) Carga el portafolio en Fase 0
3. Va a Fase 1 - IRL
4. Evalúa proyectos
5. Descarga archivo de evaluación IRL
6. Comparte archivo `evaluacion_IRL_ProyectoX.xlsx`

**Persona C - Evalúa EBCT**:
1. Recibe archivo de portafolio
2. Va a Fase 2 - EBCT
3. Evalúa características
4. Descarga archivo de evaluación EBCT
5. Comparte archivo `evaluacion_EBCT_ProyectoX.xlsx`

**Persona D - Consolida y Analiza**:
1. Recibe los 3 archivos: Portafolio, IRL y EBCT
2. Va a **🔗 Consolidador**
3. Sube los 3 archivos
4. Genera archivo consolidado
5. Va a **📊 Indicadores y Seguimiento**
6. Carga el consolidado
7. Genera reportes y análisis

✅ **Resultado**: Trabajo distribuido sin conflictos, consolidación centralizada

---

## 📋 Flujo de Trabajo Visual

```
┌─────────────────────────────────────────────────────────┐
│ FASE 0: PORTAFOLIO                                      │
│ ✓ Crear/cargar proyectos                                │
│ ✓ Descargar plantilla vacía                             │
│ ✓ Descargar datos actuales                              │
│ ✓ Anexar nuevos proyectos                               │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ FASE 1: IRL (MADUREZ TECNOLÓGICA)                       │
│ ✓ 151 preguntas × 6 dimensiones                         │
│ ✓ Evaluación manual o por Excel                         │
│ ✓ Descargar plantilla pre-llenada                       │
│ ✓ Descargar evaluación actual                           │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ FASE 2: EBCT (CARACTERÍSTICAS ORGANIZACIONALES)          │
│ ✓ 34 características × 4 fases                          │
│ ✓ Estados: Verde, Amarillo, Rojo                        │
│ ✓ Plan de acción con fechas                             │
│ ✓ Descargar evaluación actual                           │
└────────────────┬────────────────────────────────────────┘
                 ↓
       ┌─────────┴──────────┐
       │                    │
       ↓                    ↓
┌──────────────┐   ┌────────────────┐
│ OPCIÓN A:    │   │ OPCIÓN B:      │
│ Sesión única │   │ Consolidar     │
│ ↓            │   │ archivos       │
│ Indicadores  │   │ separados      │
└──────────────┘   └────────┬───────┘
                            ↓
                   ┌────────────────┐
                   │ CONSOLIDADOR   │
                   │ Combina 3      │
                   │ archivos       │
                   └────────┬───────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ INDICADORES Y SEGUIMIENTO                                │
│ ✓ Vista general                                          │
│ ✓ Análisis comparativo                                   │
│ ✓ Vista individual por proyecto                          │
│ ✓ Gráficos, métricas y reportes                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Solución de Problemas

### Problema: "No se muestran proyectos en el dropdown"
**Solución**:
- Verifica que hayas cargado el portafolio en Fase 0
- Revisa el indicador de estado (debe mostrar "🟢 X proyectos cargados")
- Si está vacío, descarga y carga un archivo de portafolio

### Problema: "Error al cargar archivo Excel"
**Solución**:
- Verifica que openpyxl esté instalado
- Asegúrate de que el archivo tenga la extensión .xlsx
- No uses archivos .xls (formato antiguo)
- Verifica que las columnas requeridas existan

### Problema: "IDs inconsistentes al consolidar"
**Solución**:
- Verifica que los ID_Proyecto sean idénticos en los 3 archivos
- Los IDs son case-sensitive (mayúsculas/minúsculas importan)
- No uses espacios en los IDs

### Problema: "Respuestas VERDADERO/FALSO se convierten a TRUE/FALSE"
**Solución**:
- Descarga la **nueva plantilla** que tiene formato de texto
- No edites manualmente la celda, usa el dropdown
- Si ya tienes problemas, el sistema normaliza automáticamente

---

## 💡 Tips y Mejores Prácticas

### Para Portafolio:
- ✅ Usa IDs cortos y descriptivos: `INNO-001`, `PROJ-A`, etc.
- ✅ Mantén nombres consistentes
- ✅ Descarga respaldos antes de hacer cambios masivos
- ❌ No uses caracteres especiales en IDs: `#`, `@`, `/`

### Para Evaluaciones IRL:
- ✅ Usa la plantilla Excel (ahorra 80% del tiempo)
- ✅ Agrega evidencias detalladas para respuestas VERDADERO
- ✅ Revisa la tabla de confirmación antes de evaluar
- ❌ No cambies la estructura de la plantilla

### Para Evaluaciones EBCT:
- ✅ Evalúa fase por fase (1→2→3→4)
- ✅ Sé realista con los estados (amarillo es válido)
- ✅ Define fechas realistas en el plan de acción
- ❌ No dejes características sin evaluar

### Para Consolidación:
- ✅ Nombra archivos con fecha: `portafolio_2024 11_20.xlsx`
- ✅ Valida los IDs antes de consolidar
- ✅ Guarda el consolidado con nombre descriptivo
- ❌ No mezcles evaluaciones de diferentes momentos

---

## 📊 Interpretación de Indicadores

### IRL (Innovation Readiness Level):
- **Escala**: 1 (mínimo) a 9 (máximo)
- **6 dimensiones independientes**
- **No se promedian**: Cada dimensión es un indicador separado
- **Interpretación**:
  - 7-9: Alto nivel de madurez
  - 4-6: Nivel medio, en desarrollo
  - 1-3: Nivel bajo, requiere atención

### EBCT (Características Organizacionales):
- **34 características en 4 fases**
- **Estados**:
  - 🟢 Verde (3 puntos): Cumple
  - 🟡 Amarillo (2 puntos): En desarrollo
  - 🔴 Rojo (1 punto): No cumple
- **Cumplimiento**: % de características en verde
- **Interpretación**:
  - >70%: Excelente
  - 40-70%: Aceptable
  - <40%: Crítico

### Madurez Global:
- **Fórmula**: `(IRL_promedio/9 × 40%) + (EBCT_cumplimiento × 60%)`
- **Componentes**:
  - 40% peso madurez tecnológica (IRL)
  - 60% peso capacidades organizacionales (EBCT)
- **Resultado**: 0-100%

---

## 📞 Soporte y Contacto

Para dudas o problemas no cubiertos en este manual:
1. Revisa los tooltips (ⓘ) en la aplicación
2. Abre los expanders de ayuda en cada página
3. Consulta con el administrador del sistema

---

**Versión del Manual**: 1.0  
**Fecha**: Noviembre 2025  
**Sistema**: Gestor de Innovación - Evaluación IRL y EBCT
