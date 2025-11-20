import pandas as pd
import streamlit as st
import io
import plotly.graph_objects as go
import plotly.express as px
from html import escape
from pathlib import Path
from datetime import datetime

from core import db, utils
from core.config import DIMENSIONES_TRL
from core.data_table import render_table
from core.db_trl import get_trl_history
from core.db_ebct import (
    get_ebct_history,
    init_db_ebct,
    save_ebct_evaluation,
)
from core.ebct import (
    EBCT_CHARACTERISTICS,
    EBCT_PHASES,
    get_characteristics_by_phase,
)
from core.ebct_panel import build_phase_summary, format_weight, prepare_panel_data
from core.theme import load_theme


def _display_text(value, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        text = value.strip()
        return text if text else default
    if pd.isna(value):
        return default
    return str(value)


def generate_excel_template() -> bytes:
    """Genera un archivo Excel con la plantilla de evaluación EBCT con instructivo."""
    # Crear DataFrame con todas las características
    data = []
    for char in EBCT_CHARACTERISTICS:
        # Encontrar fase
        fase_nombre = "N/A"
        for phase in EBCT_PHASES:
            if char.get("phase_id") == phase.get("id"):
                fase_nombre = phase.get("name", "N/A")
                break
        
        data.append({
            "ID": char["id"],
            "Fase": fase_nombre,
            "Característica": char["name"],
            "Respuesta": "Seleccionar una opción",
            "Notas (opcional)": ""
        })
    
    df = pd.DataFrame(data)
    
    # Crear Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja de Instructivo
        instructivo_data = {
            "INSTRUCCIONES PARA COMPLETAR LA PLANTILLA": [
                "1. Complete la columna 'Respuesta' con una de las siguientes opciones:",
                "   • No cumple (o 🔴 No cumple)",
                "   • En desarrollo (o 🟡 En desarrollo)",  
                "   • Sí cumple (o 🟢 Sí cumple)",
                "",
                "2. Puede escribir la opción con o sin emojis",
                "",
                "3. La columna 'Notas' es opcional",
                "",
                "4. NO modifique las columnas ID, Fase ni Característica",
                "",
                "5. Una vez completado, guarde el archivo y cárguelo en la aplicación",
                "",
                "OPCIONES VÁLIDAS:",
                "─────────────────────────────────────────",
                "🔴 No cumple - La característica NO se cumple",
                "🟡 En desarrollo - La característica está EN PROCESO",
                "🟢 Sí cumple - La característica SÍ se cumple"
            ]
        }
        df_instructivo = pd.DataFrame(instructivo_data)
        df_instructivo.to_excel(writer, sheet_name='📋 Instructivo', index=False, header=False)
        
        # Hoja de Evaluación
        df.to_excel(writer, sheet_name='Evaluación EBCT', index=False)
        
        # Ajustar ancho de columnas en la hoja de Evaluación
        worksheet_eval = writer.sheets['Evaluación EBCT']
        worksheet_eval.column_dimensions['A'].width = 8
        worksheet_eval.column_dimensions['B'].width = 25
        worksheet_eval.column_dimensions['C'].width = 60
        worksheet_eval.column_dimensions['D'].width = 30
        worksheet_eval.column_dimensions['E'].width = 40
        
        # Ajustar ancho en la hoja de Instructivo
        worksheet_inst = writer.sheets['📋 Instructivo']
        worksheet_inst.column_dimensions['A'].width = 80
    
    output.seek(0)
    return output.getvalue()


def load_excel_responses(uploaded_file) -> dict:
    """Carga respuestas desde un archivo Excel y retorna un diccionario ID->Respuesta."""
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Evaluación EBCT')
        
        # Validar columnas requeridas
        required_cols = ["ID", "Respuesta"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ El Excel debe contener las columnas: {', '.join(required_cols)}")
            return {}
        
        # Crear diccionario de respuestas
        responses = {}
        valid_responses = ["No cumple", "En desarrollo", "Sí cumple", 
                          "🔴 No cumple", "🟡 En desarrollo", "🟢 Sí cumple"]
        
        for _, row in df.iterrows():
            char_id = int(row["ID"])
            respuesta = str(row["Respuesta"]).strip()
            
            # Normalizar respuesta
            if "No cumple" in respuesta or "No" in respuesta or "🔴" in respuesta:
                responses[char_id] = "🔴 No cumple"
            elif "desarrollo" in respuesta or "En" in respuesta or "🟡" in respuesta:
                responses[char_id] = "🟡 En desarrollo"
            elif "cumple" in respuesta or "Sí" in respuesta or "🟢" in respuesta:
                responses[char_id] = "🟢 Sí cumple"
            else:
                responses[char_id] = "🔴 No cumple"  # Default
        
        return responses
    except Exception as e:
        st.error(f"❌ Error al leer el archivo Excel: {str(e)}")
        return {}


def render_phase_overview(panel_map: dict[int, bool]) -> None:
    """Render a simplified EBCT phase overview without custom HTML."""

    phase_summary = build_phase_summary(panel_map)
    if phase_summary:
        summary_records = []
        for entry in phase_summary:
            total_value = entry["total_value"]
            if total_value:
                completed_label = f"{entry['achieved_label']}/{entry['total_label']}"
            else:
                completed_label = "Sin características registradas"
            summary_records.append(
                {
                    "Fase": entry["name"],
                    "Descripción": entry["subtitle"] or "—",
                    "Cumplimiento": entry["percentage_label"],
                    "Características cumplidas": completed_label,
                }
            )
        summary_df = pd.DataFrame(summary_records)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    panel_data = prepare_panel_data(panel_map)
    for data in panel_data:
        phase = data["phase"]
        phase_name = phase.get("name", "Fase")
        phase_subtitle = phase.get("subtitle", "")
        total = data["total"] or 0.0
        achieved = data["achieved"] or 0.0
        percentage = data["percentage"]
        progress_value = max(0.0, min(1.0, percentage / 100 if total else 0.0))

        with st.expander(phase_name, expanded=False):
            if phase_subtitle:
                st.caption(phase_subtitle)
            st.progress(progress_value)
            if total:
                st.write(
                    f"Cumplimiento: {percentage:.0f}% | Características logradas: "
                    f"{format_weight(achieved)} de {format_weight(total)}"
                )
            else:
                st.info("Sin características registradas para esta fase.")

            if data["items"]:
                items_df = pd.DataFrame(
                    [
                        {
                            "ID": item["id"],
                            "Característica": item["name"],
                            "Cumple": "Sí" if item["status"] else "No",
                            "Peso": format_weight(item["weight"]),
                        }
                        for item in data["items"]
                    ]
                )
                st.dataframe(
                    items_df,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No hay características asociadas a esta fase.")


OPTION_NO = "🔴 No cumple"
OPTION_PARTIAL = "🟡 En desarrollo"
OPTION_YES = "🟢 Sí cumple"

# Mapeo de opciones a valores numéricos para scoring y ayuda
OPTION_INFO = {
    OPTION_NO: {
        "score": 0.0,
        "color": "#ff4d4d",  # Rojo
        "help": "La característica no está implementada o no cumple los criterios mínimos.",
        "icon": "🔴",
    },
    OPTION_PARTIAL: {
        "score": 0.5,
        "color": "#ffd700",  # Amarillo
        "help": "La característica está en proceso de implementación o cumple parcialmente.",
        "icon": "🟡",
    },
    OPTION_YES: {
        "score": 1.0,
        "color": "#1f6b36",  # Verde
        "help": "La característica cumple completamente con los criterios establecidos.",
        "icon": "🟢",
    }
}

# Shortcuts para scoring
OPTION_SCORES = {opt: info["score"] for opt, info in OPTION_INFO.items()}

SUMMARY_SECTIONS = [
    {
        "title": "Objetivos de la Plataforma",
        "items": [
            "Guiar a Emprendimientos de Base Científico-Tecnológica (EBCT) desde la ideación hasta la internacionalización.",
            "Mostrar de forma visual e interactiva la hoja de ruta con etapas, capacidades necesarias y próximos pasos según el nivel de madurez.",
            "Facilitar la identificación de fuentes de financiamiento, programas de apoyo y actores clave del ecosistema nacional.",
            "Reducir la incertidumbre en la toma de decisiones y mejorar la gestión estratégica de las EBCT.",
            "Detectar brechas y saturación en programas de apoyo para orientar políticas públicas y coordinación interinstitucional.",
        ],
    },
    {
        "title": "Funcionalidades",
        "items": [
            "Mapa base de actores para ubicar universidades, OTLs, incubadoras, fondos y otros aliados estratégicos por región.",
            "Rutas personalizadas según la etapa tecnológica y comercial del emprendimiento a partir de un autodiagnóstico detallado.",
            "Directorio actualizado de programas y financiamiento con filtros por región y sector.",
            "Canal único de vinculación para contactar múltiples instituciones desde un mismo punto.",
            "Seguimiento y trazabilidad del avance, actores vinculados y resultados obtenidos.",
            "Visualización clara de la hoja de ruta desde la investigación hasta la exportación o escalamiento.",
        ],
    },
    {
        "title": "Público objetivo",
        "items": [
            "Equipos científicos que inician procesos de valorización tecnológica.",
            "Spin-offs universitarios en etapa de validación técnica o comercial.",
            "Startups tecnológicas que buscan clientes o inversión.",
            "EBCT consolidadas que requieren apoyo para escalar o internacionalizarse.",
            "Actores de apoyo (universidades, incubadoras, agencias públicas, inversionistas) que buscan coordinarse y acceder a información consolidada.",
        ],
    },
]

SUMMARY_FOOTER = "Agosto, 2025"


st.set_page_config(page_title="Fase 2 - Trayectoria EBCT", page_icon="🌲", layout="wide")
load_theme()
init_db_ebct()

# ========================================
# BANNER PRINCIPAL - AL INICIO DE LA PÁGINA
# ========================================
st.markdown("""
<style>
.ebct-header-banner {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(27, 94, 32, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.ebct-header-title {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
}

.ebct-header-title h1 {
    color: white;
    font-size: 2.2rem;
    margin: 0;
    font-weight: 700;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.ebct-header-subtitle {
    color: rgba(255, 255, 255, 0.98);
    font-size: 1.05rem;
    margin: 0 0 1.5rem 0;
    font-weight: 400;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}

.ebct-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.ebct-info-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.25);
    transition: all 0.3s ease;
}

.ebct-info-card:hover {
    background: rgba(255, 255, 255, 0.22);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.ebct-info-card-title {
    color: white;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.ebct-info-card-content {
    color: rgba(255, 255, 255, 0.95);
    font-size: 0.95rem;
    line-height: 1.6;
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.ebct-info-card-content ul {
    margin: 0.5rem 0;
    padding-left: 1.2rem;
}

.ebct-info-card-content li {
    margin: 0.4rem 0;
    color: rgba(255, 255, 255, 0.92);
}

.ebct-info-card-content strong {
    color: white;
    font-weight: 600;
}

.ebct-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.2rem 0.3rem 0.2rem 0;
}

.badge-red { background: rgba(244, 67, 54, 0.9); color: white; }
.badge-yellow { background: rgba(255, 193, 7, 0.9); color: #333; }
.badge-green { background: rgba(76, 175, 80, 0.9); color: white; }

.ebct-tip {
    background: rgba(255, 249, 196, 0.25);
    border-left: 4px solid #ffeb3b;
    padding: 0.8rem 1rem;
    border-radius: 8px;
    margin-top: 1rem;
    backdrop-filter: blur(5px);
}

.ebct-tip strong {
    color: #ffeb3b;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
</style>

<div class="ebct-header-banner">
<div class="ebct-header-title">
<span style="font-size: 2.5rem;">🧭</span>
<h1>Evaluación EBCT por Características</h1>
</div>
<p class="ebct-header-subtitle" style="color: white;">
Evalúa las 34 características clave de tu Emprendimiento de Base Científico-Tecnológica a través de 4 fases de desarrollo
</p>

<div class="ebct-info-grid">
<div class="ebct-info-card">
<div class="ebct-info-card-title">
<span>📋</span> ¿QUÉ ES LA EVALUACIÓN EBCT?
</div>
<div class="ebct-info-card-content">
Herramienta de diagnóstico que mide el nivel de madurez de tu emprendimiento mediante <strong>34 características distribuidas en 4 fases</strong>:
<ul style="margin-top: 0.8rem;">
<li><strong>Fase Incipiente:</strong> Validación técnica y científica</li>
<li><strong>Validación y PI:</strong> Protección intelectual</li>
<li><strong>Preparación para Mercado:</strong> Modelo de negocio</li>
<li><strong>Internacionalización:</strong> Expansión global</li>
</ul>
</div>
</div>

<div class="ebct-info-card">
<div class="ebct-info-card-title">
<span>📝</span> INSTRUCCIONES DE USO
</div>
<div class="ebct-info-card-content">
<strong>Paso 1:</strong> Navega por las pestañas de cada fase<br>
<strong>Paso 2:</strong> Evalúa cada característica según su estado actual:<br>
<div style="margin: 0.8rem 0;">
<span class="ebct-badge badge-red">🔴 No cumple</span>
<span class="ebct-badge badge-yellow">🟡 En desarrollo</span>
<span class="ebct-badge badge-green">🟢 Sí cumple</span>
</div>
<strong>Paso 3:</strong> Guarda tu evaluación para generar el semáforo visual y panel de trayectoria
</div>
</div>

<div class="ebct-info-card">
<div class="ebct-info-card-title">
<span>⚡</span> CARGA MASIVA CON EXCEL
</div>
<div class="ebct-info-card-content">
<strong>Descarga la plantilla Excel</strong> con las 34 características pre-cargadas<br>
<strong>Completa offline</strong> marcando el estado de cada característica<br>
<strong>Carga el archivo</strong> para aplicar todas las respuestas automáticamente
<div class="ebct-tip">
<strong>💡 Tip:</strong> Ideal para evaluaciones en equipo o cuando necesitas revisar documentación antes de responder
</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .page-intro {
        display: grid;
        grid-template-columns: minmax(0, 1.7fr) minmax(0, 1fr);
        gap: 2.4rem;
        padding: 2.3rem 2.6rem;
        border-radius: 30px;
        background: linear-gradient(145deg, rgba(18, 48, 29, 0.9), rgba(111, 75, 44, 0.86));
        color: #fdf9f2;
        box-shadow: 0 36px 60px rgba(12, 32, 20, 0.35);
        margin-bottom: 2.6rem;
    }

    .page-intro h1 {
        font-size: 2.2rem;
        margin-bottom: 1rem;
        color: #fffdf8;
    }

    .page-intro p {
        font-size: 1.02rem;
        line-height: 1.6;
        color: rgba(253, 249, 242, 0.86);
    }

    .page-intro__aside {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .page-intro__aside .intro-stat {
        background: rgba(255, 255, 255, 0.14);
        border-radius: 20px;
        padding: 1.1rem 1.3rem;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
    }

    .page-intro__aside .intro-stat strong {
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-size: 0.9rem;
        margin-bottom: 0.35rem;
        color: #fefcf9;
    }

    .page-intro__aside .intro-stat p {
        margin: 0;
        color: rgba(253, 249, 242, 0.86);
        font-size: 0.96rem;
        line-height: 1.5;
    }

    .back-band {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1.6rem;
    }

    .section-shell {
        background: #ffffff;
        border-radius: 24px;
        padding: 1.6rem 1.8rem;
        border: 1px solid rgba(var(--shadow-color), 0.12);
        box-shadow: 0 24px 48px rgba(var(--shadow-color), 0.16);
        margin-bottom: 2.3rem;
    }

    .section-shell h3, .section-shell h4 {
        margin-top: 0;
    }

    .selection-card {
        position: relative;
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
        border: 2px solid #1b5e20;
        box-shadow: 0 4px 16px rgba(27, 94, 32, 0.12), 0 2px 6px rgba(0,0,0,0.06);
        overflow: hidden;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }

    .selection-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(27, 94, 32, 0.16), 0 3px 8px rgba(0,0,0,0.08);
    }

    .selection-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #1b5e20 0%, #43a047 50%, #1b5e20 100%);
    }

    .selection-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(27,94,32,0.04) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .selection-card__badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.72rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(27, 94, 32, 0.25);
        position: relative;
        z-index: 2;
    }

    .selection-card__badge::before {
        content: '✓';
        font-size: 0.85rem;
        font-weight: 900;
    }

    .selection-card__title {
        margin: 0.8rem 0 0.4rem;
        font-size: 1.4rem;
        font-weight: 700;
        color: #1b5e20;
        line-height: 1.3;
        position: relative;
        z-index: 2;
    }

    .selection-card__subtitle {
        margin: 0 0 1rem;
        color: #2e7d32;
        font-size: 1rem;
        font-weight: 500;
        position: relative;
        z-index: 2;
    }

    .selection-card__meta {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 0.7rem;
        margin-top: 1rem;
        position: relative;
        z-index: 2;
    }

    .selection-card__meta-item {
        padding: 0.7rem 0.9rem;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid rgba(27, 94, 32, 0.15);
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        backdrop-filter: blur(4px);
        transition: background 150ms ease, border-color 150ms ease;
    }

    .selection-card__meta-item:hover {
        background: rgba(255, 255, 255, 0.95);
        border-color: rgba(27, 94, 32, 0.25);
    }

    .selection-card__meta-label {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.5px;
        font-weight: 700;
        color: #5a7d5e;
        margin-bottom: 0.3rem;
    }

    .selection-card__meta-label::before {
        content: '▪';
        color: #43a047;
        font-size: 0.9rem;
    }

    .selection-card__meta-value {
        display: block;
        font-size: 1rem;
        font-weight: 600;
        color: #1b3c1f;
        line-height: 1.3;
    }

    .ebct-summary {
        background: #ffffff;
        border-radius: 26px;
        padding: 1.8rem 2rem;
        border: 1px solid rgba(var(--shadow-color), 0.12);
        box-shadow: 0 24px 48px rgba(var(--shadow-color), 0.14);
        margin-bottom: 2.3rem;
    }

    .ebct-summary__grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.4rem;
    }

    .ebct-summary__column h4 {
        margin: 0 0 0.65rem;
        font-size: 1rem;
        color: var(--forest-900);
    }

    .ebct-summary__column ul {
        margin: 0;
        padding-left: 1.1rem;
        display: grid;
        gap: 0.55rem;
        color: var(--text-700);
    }

    .ebct-summary__column li {
        line-height: 1.45;
    }

    .ebct-summary__footer {
        margin-top: 1.4rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 1.1rem;
        border-radius: 999px;
        background: rgba(var(--shadow-color), 0.08);
        color: var(--forest-700);
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    .ebct-roadmap {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1.6rem;
        margin-top: 1.4rem;
    }

    .ebct-phase {
        border-radius: 24px;
        border: 1px solid rgba(var(--shadow-color), 0.12);
        box-shadow: 0 24px 48px rgba(var(--shadow-color), 0.12);
        background: #ffffff;
        overflow: hidden;
        border-top: 4px solid var(--phase-accent, var(--forest-500));
        display: flex;
        flex-direction: column;
    }

    .ebct-phase__header {
        padding: 1.2rem 1.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        background: linear-gradient(135deg, rgba(var(--shadow-color), 0.06), rgba(var(--shadow-color), 0.03));
    }

    .ebct-phase__header h4 {
        margin: 0;
        font-size: 1.05rem;
        color: var(--forest-900);
    }

    .ebct-phase__header span {
        display: block;
        font-size: 0.85rem;
        color: var(--text-500);
    }

    .ebct-phase__score {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.18rem;
    }

    .ebct-phase__score strong {
        font-size: 1.35rem;
        color: var(--phase-accent, var(--forest-700));
    }

    .ebct-phase__score span {
        font-size: 0.78rem;
        color: var(--text-500);
        letter-spacing: 0.2px;
    }

    .ebct-phase__items {
        padding: 1.2rem 1.4rem 1.6rem;
        display: grid;
        gap: 0.9rem;
    }

    .ebct-chip {
        border-radius: 18px;
        padding: 0.85rem 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        background: rgba(255, 255, 255, 0.94);
        border: 1px dashed rgba(var(--shadow-color), 0.22);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .ebct-chip--yes {
        background: linear-gradient(135deg, var(--chip-color-start), var(--chip-color-end));
        border: none;
        color: var(--forest-950);
        box-shadow: 0 18px 32px rgba(var(--shadow-color), 0.18);
    }

    .ebct-chip--no {
        color: var(--text-700);
    }

    .ebct-chip__title {
        font-weight: 600;
        font-size: 0.95rem;
    }

    .ebct-chip small {
        font-size: 0.75rem;
        color: rgba(var(--shadow-color), 0.65);
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    .ebct-chip:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 34px rgba(var(--shadow-color), 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

fase1_page = next(Path("pages").glob("03_*_Fase_1_*.py"), None)
if fase1_page:
    st.markdown("<div class='back-band'>", unsafe_allow_html=True)
    if st.button("Volver a Fase 1", type="primary"):
        st.switch_page(str(fase1_page))
    st.markdown("</div>", unsafe_allow_html=True)

payload = st.session_state.get("fase2_payload")
fase2_ready = st.session_state.get("fase2_ready", False)

if not payload or not fase2_ready:
    st.warning("Finaliza una evaluación en Fase 1 para acceder a esta etapa.")
    if fase1_page:
        if st.button("Ir a Fase 1", key="fase2_btn_ir_fase1"):
            st.switch_page(str(fase1_page))
    st.stop()

project_id = payload.get("project_id")
if project_id is None:
    st.error("No se pudo determinar el proyecto seleccionado desde Fase 1.")
    st.stop()

previous_project = st.session_state.get("fase2_active_project_id")
if previous_project is not None and previous_project != project_id:
    for item in EBCT_CHARACTERISTICS:
        st.session_state.pop(f"ebct_resp_{item['id']}", None)
    st.session_state.pop("ebct_panel_map", None)
    st.session_state.pop("ebct_last_eval_timestamp", None)
st.session_state["fase2_active_project_id"] = project_id

history_df = get_ebct_history(project_id)
last_eval_map: dict[int, bool] | None = None
last_eval_timestamp: str | None = None
if not history_df.empty:
    last_eval_timestamp = history_df["fecha_eval"].iloc[0]
    latest_eval_df = history_df[history_df["fecha_eval"] == last_eval_timestamp]
    last_eval_map = {
        int(row["caracteristica_id"]): bool(row["cumple"])
        for _, row in latest_eval_df.iterrows()
    }
    st.session_state["ebct_last_eval_timestamp"] = last_eval_timestamp

panel_map = st.session_state.get("ebct_panel_map")
if panel_map is None and last_eval_map:
    panel_map = last_eval_map.copy()
    st.session_state["ebct_panel_map"] = panel_map

for item in EBCT_CHARACTERISTICS:
    key = f"ebct_resp_{item['id']}"
    if key not in st.session_state:
        default_value = OPTION_YES if last_eval_map and last_eval_map.get(item["id"]) else OPTION_NO
        st.session_state[key] = default_value

responses_records = payload.get("responses", [])
irl_score = payload.get("irl_score")
fecha_eval = payload.get("fecha_eval")

order_map = {item["id"]: idx for idx, item in enumerate(DIMENSIONES_TRL)}
label_map = {item["id"]: item.get("label", item["id"]) for item in DIMENSIONES_TRL}

responses_df = pd.DataFrame(responses_records)
if not responses_df.empty:
    responses_df["__order"] = responses_df["dimension"].map(order_map)
    responses_df = responses_df.sort_values(["__order", "nivel"], ascending=[True, False])
    responses_df = responses_df.drop(columns="__order")
    responses_df["dimension_label"] = responses_df["dimension"].map(label_map)
    responses_df["dimension_label"] = responses_df["dimension_label"].fillna(responses_df["dimension"])
    responses_df = responses_df.drop(columns="dimension")
    responses_df = responses_df.rename(
        columns={
            "dimension_label": "Dimensión",
            "nivel": "Nivel acreditado",
            "evidencia": "Evidencia",
        }
    )
    responses_df["Nivel acreditado"] = pd.to_numeric(
        responses_df["Nivel acreditado"], errors="coerce"
    ).astype("Int64")
    responses_df = responses_df[["Dimensión", "Nivel acreditado", "Evidencia"]]


snapshot = payload.get("project_snapshot", {}).copy()
df_port = utils.normalize_df(db.fetch_df())
project_row = df_port.loc[df_port["id_innovacion"] == project_id]
if not project_row.empty:
    row = project_row.iloc[0]
    for field in (
        "nombre_innovacion",
        "potencial_transferencia",
        "impacto",
        "estatus",
        "responsable_innovacion",
    ):
        value = row.get(field)
        if isinstance(value, str):
            value = value.strip()
        if value not in (None, "") and not (isinstance(value, float) and pd.isna(value)):
            snapshot[field] = value
    eval_value = row.get("evaluacion_numerica")
    if eval_value not in (None, "") and not pd.isna(eval_value):
        snapshot["evaluacion_numerica"] = float(eval_value)

nombre_txt = _display_text(snapshot.get("nombre_innovacion"), "Proyecto seleccionado")
transferencia_txt = _display_text(snapshot.get("potencial_transferencia"), "Sin potencial declarado")
impacto_txt = _display_text(snapshot.get("impacto"), "No informado")
estado_txt = _display_text(snapshot.get("estatus"), "Sin estado")
responsable_txt = _display_text(snapshot.get("responsable_innovacion"), "Sin responsable asignado")
evaluacion_val = snapshot.get("evaluacion_numerica")
evaluacion_txt = (
    f"{float(evaluacion_val):.1f}" if evaluacion_val is not None and not pd.isna(evaluacion_val) else "—"
)

selection_meta = [
    ("Impacto estratégico", impacto_txt),
    ("Estado actual", estado_txt),
    ("Responsable de innovación", responsable_txt),
    ("Evaluación Fase 0", evaluacion_txt),
]

meta_items_html = "".join(
    f"<div class='selection-card__meta-item'>"
    f"<span class='selection-card__meta-label'>{escape(label)}</span>"
    f"<span class='selection-card__meta-value'>{escape(str(value))}</span>"
    "</div>"
    for label, value in selection_meta
)

selection_card_html = f"""
<div class='selection-card'>
    <span class='selection-card__badge'>Proyecto seleccionado</span>
    <h3 class='selection-card__title'>{escape(nombre_txt)}</h3>
    <p class='selection-card__subtitle'>{escape(str(transferencia_txt))}</p>
    <div class='selection-card__meta'>
        {meta_items_html}
    </div>
</div>
"""

# ========================================
# SECCIÓN LIMPIA: Solo mostrar info del proyecto seleccionado
# ========================================

# Opcional: Expandible con contexto de la plataforma (objetivos, funcionalidades, público)
with st.expander("📖 Sobre la Plataforma EBCT", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Objetivos de la Plataforma")
        for item in SUMMARY_SECTIONS[0]["items"]:
            st.markdown(f"- {item}")
    
    with col2:
        st.markdown("#### ⚙️ Funcionalidades")
        for item in SUMMARY_SECTIONS[1]["items"]:
            st.markdown(f"- {item}")
    
    with col3:
        st.markdown("#### 👥 Público objetivo")
        for item in SUMMARY_SECTIONS[2]["items"]:
            st.markdown(f"- {item}")
    
    st.caption(f"_{SUMMARY_FOOTER}_")

# Información del proyecto seleccionado
with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown(selection_card_html, unsafe_allow_html=True)
    if fecha_eval:
        st.caption(f"Evaluación IRL registrada el {fecha_eval}.")
    st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# INICIALIZAR VALORES POR DEFECTO ANTES DE CREAR WIDGETS
# ========================================

# Procesar reset si fue solicitado
if st.session_state.get('reset_triggered', False):
    # Limpiar todos los estados de respuesta
    for item in EBCT_CHARACTERISTICS:
        key = f"ebct_resp_{item['id']}"
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.reset_triggered = False
    st.session_state.show_reset_message = True

# Inicializar todas las respuestas con "No cumple" si no existen
for item in EBCT_CHARACTERISTICS:
    key = f"ebct_resp_{item['id']}"
    if key not in st.session_state:
        st.session_state[key] = "🔴 No cumple"

# Variable para controlar si se cargó un archivo
if 'excel_loaded' not in st.session_state:
    st.session_state.excel_loaded = False

# ========================================
# BOTONES DE CARGA/DESCARGA EXCEL
# ========================================
# SECCIÓN DE CARGA/DESCARGA DE PLANTILLA EXCEL
# ========================================
st.markdown("### 📊 Gestión de Respuestas Excel")
st.caption("Descarga la plantilla, complétala offline y cárgala aquí para importar todas las respuestas de una vez")

col_download, col_upload = st.columns([1, 1])

with col_download:
    # Botón de descarga con instructivo
    excel_data = generate_excel_template()
    st.download_button(
        label="📥 Descargar plantilla Excel",
        data=excel_data,
        file_name=f"EBCT_Plantilla_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Descarga la plantilla Excel con instructivo incluido. Incluye las 3 opciones de respuesta.",
        use_container_width=True
    )
    st.caption("✓ Incluye instructivo con las 3 opciones de respuesta")

with col_upload:
    # Botón de carga del archivo Excel
    uploaded_file = st.file_uploader(
        "📤 Seleccionar archivo Excel",
        type=["xlsx", "xls"],
        help="Selecciona el archivo Excel con las respuestas completadas",
        label_visibility="visible",
        key="excel_uploader"
    )
    
    # Procesar archivo cargado (solo leer, no aplicar aún)
    if uploaded_file is not None:
        responses = load_excel_responses(uploaded_file)
        if responses:
            # Guardar en session_state para revisión
            st.session_state.pending_excel_responses = responses
            st.session_state.excel_file_loaded = True
            st.info(f"📄 Archivo cargado: {len(responses)} respuestas encontradas")
    else:
        # Si no hay archivo, limpiar respuestas pendientes
        if 'pending_excel_responses' in st.session_state:
            del st.session_state.pending_excel_responses
        if 'excel_file_loaded' in st.session_state:
            del st.session_state.excel_file_loaded

# Botón para aplicar las respuestas del Excel
if st.session_state.get('excel_file_loaded', False) and 'pending_excel_responses' in st.session_state:
    st.info(f"📋 **{len(st.session_state.pending_excel_responses)} respuestas** listas para aplicar. Haz clic en el botón para cargarlas en el cuestionario.")
    
    if st.button("✅ Aplicar respuestas al cuestionario", use_container_width=True, type="primary"):
        # Aplicar todas las respuestas al session_state
        for char_id, respuesta in st.session_state.pending_excel_responses.items():
            key = f"ebct_resp_{char_id}"
            st.session_state[key] = respuesta
        
        st.session_state.excel_applied = True
        # Limpiar pendientes
        del st.session_state.pending_excel_responses
        del st.session_state.excel_file_loaded
        # No hacer rerun aquí - el mensaje se mostrará en el siguiente render natural

# Mostrar confirmación si se aplicaron respuestas (sin rerun)
if st.session_state.get('excel_applied', False):
    st.success("✅ Respuestas aplicadas correctamente. Ahora puedes modificarlas manualmente en el cuestionario o guardar la evaluación.")
    st.session_state.excel_applied = False

# Espacio antes del contenido principal
st.markdown("<br>", unsafe_allow_html=True)

# ========================================
# SECCIÓN DE EVALUACIÓN
# ========================================
with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)

    grouped_characteristics = get_characteristics_by_phase()
    
    # Definir colores y porcentajes de dimensiones
    DIMENSION_COLORS = {
        1: {"color": "#673AB7", "name": "Investigación y Validación Técnica"},  # Purpura
        2: {"color": "#4CAF50", "name": "Estrategia de Propiedad Intelectual"},  # Verde
        3: {"color": "#2196F3", "name": "Estrategia de Desarrollo de Negocio", "pct": 0.30},  # Azul
        4: {"color": "#2196F3", "name": "Modelo de Negocio", "pct": 0.30},  # Azul
        5: {"color": "#2196F3", "name": "Estrategia Comercial", "pct": 0.40},  # Azul
        6: {"color": "#FFC107", "name": "Estrategia y Gestión para Exportación"}  # Amarillo
    }

    # Mapeo de dimensión -> fase (para tooltips claros por dimensión)
    DIMENSION_PHASE_LABELS = {
        1: "Fase Incipiente / Validación técnica",
        2: "Fase Validación y PI",
        3: "Fase Preparación para Mercado",
        4: "Fase Preparación para Mercado",
        5: "Fase Preparación para Mercado",
        6: "Fase Internacionalización",
    }

    # Mapeo de características a dimensiones
    CARACTERISTICA_DIMENSIONES = {
        1: [3,4,5], 2: [1], 3: [1], 4: [1], 5: [1], 6: [1], 7: [6,3,4,5], 8: [6,3,4,5],
        9: [3,4,5], 10: [1], 11: [1], 12: [6,2], 13: [2], 14: [2], 15: [6], 16: [6,3,4,5],
        17: [6], 18: [3,4,5], 19: [6,3,4,5], 20: [6], 21: [6,3,4,5], 22: [6], 23: [3,4,5],
        24: [3,4,5], 25: [3,4,5], 26: [3,4,5], 27: [3,4,5], 28: [6,3,4,5], 29: [6,3,4,5],
        30: [6], 31: [6], 32: [6], 33: [6], 34: [6]
    }

    st.markdown("""
        <style>
        .ebct-map-container {
            display: flex;
            flex-direction: column;
            gap: 2rem;
            padding: 1rem;
        }
        
        .phase-section {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding: 1.5rem;
            border-radius: 15px;
            position: relative;
        }
        
        .phase-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .phase-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }
        
        .characteristic-card {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            position: relative;
        }
        
        .dimension-indicators {
            display: flex;
            gap: 0.3rem;
            align-items: center;
        }
        
        .dimension-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .characteristic-title {
            font-size: 0.9rem;
            color: #333;
            line-height: 1.3;
        }
        
        .characteristic-options {
            padding: 0.5rem 0;
        }
        
        .dimension-tooltip {
            display: none;
            position: absolute;
            bottom: 100%;
            left: 0;
            background: white;
            padding: 0.5rem;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 1000;
            min-width: 200px;
        }
        
        .dimension-dot-container:hover .dimension-tooltip {
            display: block;
        }

        /* Colores específicos para cada fase */
        .phase-incipiente {
            background: rgba(103, 58, 183, 0.1);
            border: 1px solid rgba(103, 58, 183, 0.3);
        }
        .phase-incipiente .phase-title {
            background: #673AB7;
        }
        
        .phase-validacion {
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        .phase-validacion .phase-title {
            background: #4CAF50;
        }
        
        .phase-preparacion {
            background: rgba(33, 150, 243, 0.1);
            border: 1px solid rgba(33, 150, 243, 0.3);
        }
        .phase-preparacion .phase-title {
            background: #2196F3;
        }
        
        .phase-internacionalizacion {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
        }
        .phase-internacionalizacion .phase-title {
            background: #FFC107;
            color: #333;
        }
        
        /* Estilo compacto para características */
        .ebct-caracteristica {
            display: flex;
            align-items: center;
            padding: 0.5rem 0.8rem;
            margin-bottom: 0.3rem;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #d32f2f;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            gap: 0.8rem;
        }
        
        .ebct-id {
            font-weight: 700;
            color: #666;
            min-width: 30px;
            font-size: 0.85rem;
        }
        
        .ebct-nombre {
            flex: 1;
            color: #d32f2f;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .ebct-dimensiones {
            display: flex;
            gap: 0.3rem;
            min-width: fit-content;
            font-size: 0.85rem;
        }
        
        .ebct-respuestas {
            min-width: fit-content;
            display: flex;
            align-items: center;
        }
        
        .dim-badge {
            font-size: 0.75rem;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            background: rgba(0,0,0,0.05);
        }
        
        /* Tabs compactos */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        /* Estilos para radio buttons según opción */
        /* Contenedor de radio buttons */
        .stRadio > div {
            gap: 1rem !important;
            flex-wrap: nowrap !important;
        }
        
        /* ============================================
           SOLUCIÓN DEFINITIVA: OCULTAR RADIO NATIVO
           Y CREAR INDICADOR PERSONALIZADO EN ROJO
           ============================================ */
        
        /* OCULTAR completamente el radio button nativo de Streamlit */
        .stRadio > div > label:first-child [data-baseweb="radio"],
        .stRadio > div > label:first-child div[role="radio"],
        .stRadio > div > label:first-child input[type="radio"] {
            opacity: 0 !important;
            position: absolute !important;
            pointer-events: none !important;
        }
        
        /* Crear un círculo ROJO personalizado con ::before */
        .stRadio > div > label:first-child {
            position: relative !important;
            padding-left: 2rem !important; /* Espacio para el círculo personalizado */
        }
        
        /* Círculo ROJO personalizado (no seleccionado) */
        .stRadio > div > label:first-child::before {
            content: '' !important;
            position: absolute !important;
            left: 0.5rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            width: 16px !important;
            height: 16px !important;
            border: 2px solid #d32f2f !important;
            border-radius: 50% !important;
            background-color: transparent !important;
            transition: all 0.2s ease !important;
        }
        
        /* Punto ROJO interno cuando está seleccionado */
        .stRadio > div > label:first-child::after {
            content: '' !important;
            position: absolute !important;
            left: 0.75rem !important;
            top: 50% !important;
            transform: translateY(-50%) scale(0) !important;
            width: 8px !important;
            height: 8px !important;
            border-radius: 50% !important;
            background-color: #d32f2f !important;
            transition: transform 0.2s ease !important;
        }
        
        /* Cuando el label tiene data-checked, mostrar el punto interno */
        .stRadio > div > label:first-child[data-checked="true"]::after {
            transform: translateY(-50%) scale(1) !important;
        }
        
        /* Si Streamlit usa un div con aria-checked, también aplicar */
        .stRadio > div > label:first-child:has([aria-checked="true"])::after {
            transform: translateY(-50%) scale(1) !important;
        }
        
        /* Radio button "No cumple" - ROJO */
        .stRadio > div > label:first-child {
            background: rgba(211, 47, 47, 0.08) !important;
            border: 2px solid #d32f2f !important;
            border-radius: 8px !important;
            padding: 0.3rem 0.6rem !important;
            transition: all 0.2s ease !important;
            margin: 0 !important;
        }
        
        .stRadio > div > label:first-child:hover {
            background: rgba(211, 47, 47, 0.15) !important;
            transform: scale(1.02);
        }
        
        .stRadio > div > label:first-child span {
            color: #d32f2f !important;
            font-weight: 600 !important;
        }
        
        /* Radio button seleccionado "No cumple" */
        .stRadio > div > label:first-child[data-checked="true"] {
            background: #d32f2f !important;
            border-color: #b71c1c !important;
        }
        
        .stRadio > div > label:first-child[data-checked="true"] span {
            color: white !important;
        }
        
        /* Radio button "En desarrollo" - AMARILLO */
        .stRadio > div > label:nth-child(2) {
            background: rgba(255, 193, 7, 0.08) !important;
            border: 2px solid #ffc107 !important;
            border-radius: 8px !important;
            padding: 0.3rem 0.6rem !important;
            transition: all 0.2s ease !important;
            margin: 0 !important;
        }
        
        .stRadio > div > label:nth-child(2):hover {
            background: rgba(255, 193, 7, 0.15) !important;
            transform: scale(1.02);
        }
        
        .stRadio > div > label:nth-child(2) span {
            color: #f57c00 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }
        
        /* Radio button seleccionado "En desarrollo" */
        .stRadio > div > label:nth-child(2)[data-checked="true"] {
            background: #ffc107 !important;
            border-color: #f57c00 !important;
        }
        
        .stRadio > div > label:nth-child(2)[data-checked="true"] span {
            color: #333 !important;
        }
        
        /* Radio button "Sí cumple" - VERDE */
        .stRadio > div > label:nth-child(3) {
            background: rgba(76, 175, 80, 0.08) !important;
            border: 2px solid #4caf50 !important;
            border-radius: 8px !important;
            padding: 0.3rem 0.6rem !important;
            transition: all 0.2s ease !important;
            margin: 0 !important;
        }
        
        .stRadio > div > label:nth-child(3):hover {
            background: rgba(76, 175, 80, 0.15) !important;
            transform: scale(1.02);
        }
        
        .stRadio > div > label:nth-child(3) span {
            color: #2e7d32 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }
        
        /* Radio button seleccionado "Sí cumple" */
        .stRadio > div > label:nth-child(3)[data-checked="true"] {
            background: #4caf50 !important;
            border-color: #2e7d32 !important;
        }
        
        .stRadio > div > label:nth-child(3)[data-checked="true"] span {
            color: white !important;
        }
        
        /* Ajustar texto de radio buttons */
        .stRadio > div > label span {
            font-size: 0.85rem !important;
        }
        </style>
        
        <script>
        // JavaScript para controlar el indicador visual ROJO personalizado
        (function() {
            function updateRadioIndicators() {
                setTimeout(function() {
                    // Procesar todos los grupos de radio buttons
                    const radioGroups = document.querySelectorAll('.stRadio');
                    
                    radioGroups.forEach(function(group) {
                        const labels = group.querySelectorAll('label');
                        
                        labels.forEach(function(label, index) {
                            // Verificar si este radio está seleccionado
                            const input = label.querySelector('input[type="radio"]');
                            const basewebRadio = label.querySelector('[data-baseweb="radio"]');
                            const roleRadio = label.querySelector('[role="radio"]');
                            
                            let isChecked = false;
                            
                            // Múltiples formas de detectar si está seleccionado
                            if (input && input.checked) {
                                isChecked = true;
                            } else if (basewebRadio && basewebRadio.getAttribute('aria-checked') === 'true') {
                                isChecked = true;
                            } else if (roleRadio && roleRadio.getAttribute('aria-checked') === 'true') {
                                isChecked = true;
                            }
                            
                            // Aplicar o remover el atributo data-checked
                            if (isChecked) {
                                label.setAttribute('data-checked', 'true');
                            } else {
                                label.removeAttribute('data-checked');
                            }
                        });
                    });
                }, 50);
            }
            
            // Aplicar al cargar
            updateRadioIndicators();
            
            // Re-aplicar cuando cambie el DOM
            const observer = new MutationObserver(updateRadioIndicators);
            observer.observe(document.body, { 
                childList: true, 
                subtree: true, 
                attributes: true,
                attributeFilter: ['aria-checked', 'checked']
            });
            
            // También escuchar clics en toda la página
            document.addEventListener('click', function() {
                updateRadioIndicators();
            });
            
            // Escuchar cambios en inputs
            document.addEventListener('change', function(e) {
                if (e.target.type === 'radio') {
                    updateRadioIndicators();
                }
            });
        })();
        </script>
    """, unsafe_allow_html=True)

    # ==== Función Semáforo (definida antes del formulario) ====
    def compute_semaforo(responses_map: dict[int, float]) -> pd.DataFrame:
        """Genera una tabla tipo semáforo a partir del mapa de respuestas.

        Lógica integrada:
        - Sí cumple (1.0) -> Verde
        - En proceso (0.5) -> Amarillo
        - No cumple (0.0) -> Rojo
        """
        rows = []
        for item in EBCT_CHARACTERISTICS:
            cid = item["id"]
            name = item["name"]
            phase = item.get("phase_name") or item.get("phase_id")
            weight = item.get("weight", 1)
            if cid in responses_map:
                score = responses_map[cid]
                if score >= 0.9:
                    estado = "🟢 Verde"
                elif score >= 0.4:
                    estado = "🟡 Amarillo"
                else:
                    estado = "🔴 Rojo"
            else:
                estado = "🟡 Amarillo"
                score = 0.5
            # Obtener dimensiones de la característica
            dims = CARACTERISTICA_DIMENSIONES.get(cid, [])
            dimension_labels = []
            for dim_id in dims:
                if dim_id == 1:
                    dimension_labels.append("🟣 Investigación y Validación Técnica")
                elif dim_id == 2:
                    dimension_labels.append("🟢 Estrategia de Propiedad Intelectual")
                elif dim_id in [3, 4, 5]:
                    dimension_labels.append(f"🔵 {DIMENSION_COLORS[dim_id]['name']} ({DIMENSION_COLORS[dim_id]['pct']*100:.0f}%)")
                elif dim_id == 6:
                    dimension_labels.append("🟡 Estrategia y Gestión para Exportación")
            
            rows.append({
                "id": cid,
                "Característica": name,
                "Fase": phase,
                "Dimensiones": " | ".join(dimension_labels),
                "Peso": weight,
                "Cumple": "Sí" if responses_map.get(cid) else "No",
                "EstadoSemaforo": estado,
                "Score": score,
            })
        return pd.DataFrame(rows)

    with st.form("fase2_ebct_form"):
        # Leyenda compacta
        with st.expander("ℹ️ Leyenda de Dimensiones", expanded=False):
            st.markdown("🟣 Inv. y Validación Técnica | 🟢 Propiedad Intelectual | 🔵 Preparación Mercado | 🟡 Exportación")
        
        # Pestañas por fase
        phase_names = [f"{p['name']}" for p in EBCT_PHASES]
        tabs = st.tabs(phase_names)
        
        for tab_idx, (tab, phase) in enumerate(zip(tabs, EBCT_PHASES)):
            with tab:
                characteristics = grouped_characteristics.get(phase["id"], [])
                if not characteristics:
                    st.info("No hay características para esta fase.")
                    continue
                
                # Mostrar características en formato compacto
                for item in characteristics:
                    # Obtener dimensiones
                    dims = CARACTERISTICA_DIMENSIONES.get(item['id'], [])
                    dim_badges = []
                    for dim_id in dims:
                        if dim_id == 1:
                            dim_badges.append("🟣")
                        elif dim_id == 2:
                            dim_badges.append("🟢")
                        elif dim_id in [3, 4, 5]:
                            pct = int(DIMENSION_COLORS[dim_id].get('pct', 0) * 100)
                            dim_badges.append(f"🔵{pct}%")
                        elif dim_id == 6:
                            dim_badges.append("🟡")
                    
                    dims_html = " ".join(dim_badges)
                    
                    # Usar columnas para alinear pregunta y respuestas en la misma línea
                    col_pregunta, col_respuesta = st.columns([0.65, 0.35])
                    
                    with col_pregunta:
                        # Contenedor compacto de pregunta
                        st.markdown(f"""
                            <div class='ebct-caracteristica'>
                                <span class='ebct-id'>{item['id']}</span>
                                <span class='ebct-nombre'>{item['name']}</span>
                                <span class='ebct-dimensiones'>{dims_html}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_respuesta:
                        # Radio buttons alineado a la derecha
                        key = f"ebct_resp_{item['id']}"
                        option = st.radio(
                            f"Respuesta para {item['id']}",
                            (OPTION_NO, OPTION_PARTIAL, OPTION_YES),
                            key=key,
                            horizontal=True,
                            label_visibility="collapsed"
                        )

        # Botones de acción - dentro del formulario, fuera del bucle de fases
        col_submit, col_reset, col_semaforo = st.columns([1, 1, 1])
        submit_clicked = col_submit.form_submit_button("💾 Guardar evaluación EBCT")
        reset_clicked = col_reset.form_submit_button("🔄 Restablecer a 'No cumple'")
        generate_semaforo = col_semaforo.form_submit_button("🚦 Generar semáforo")
        
    # JavaScript para mantener la posición del scroll
    st.markdown("""
        <script>
        // Guardar posición antes de rerun
        window.addEventListener('beforeunload', function() {
            sessionStorage.setItem('scrollPos', window.scrollY);
        });
        
        // Restaurar posición después de rerun
        document.addEventListener('DOMContentLoaded', function() {
            const scrollPos = sessionStorage.getItem('scrollPos');
            if (scrollPos) {
                window.scrollTo(0, parseInt(scrollPos));
                sessionStorage.removeItem('scrollPos');
            }
        });
        
        // Para Streamlit rerun (no recarga completa)
        const savedScroll = sessionStorage.getItem('scrollPos');
        if (savedScroll) {
            setTimeout(function() {
                window.scrollTo(0, parseInt(savedScroll));
                sessionStorage.removeItem('scrollPos');
            }, 100);
        }
        
        // Guardar posición al hacer clic en botones
        document.querySelectorAll('button').forEach(function(btn) {
            btn.addEventListener('click', function() {
                sessionStorage.setItem('scrollPos', window.scrollY);
            });
        });
        </script>
    """, unsafe_allow_html=True)
    
    # Mostrar mensaje de reset si corresponde
    if st.session_state.get('show_reset_message', False):
        st.info("✅ Se restablecieron todas las respuestas a '🔴 No cumple'.")
        st.session_state.show_reset_message = False
    
    if reset_clicked:
        # Guardar posición del scroll antes de resetear
        st.session_state.reset_triggered = True
        st.rerun()

    if submit_clicked:
        responses_map: dict[int, float] = {}
        evaluation_rows = []
        for item in EBCT_CHARACTERISTICS:
            key = f"ebct_resp_{item['id']}"
            option = st.session_state.get(key, "🔴 No cumple")
            score = OPTION_SCORES.get(option, 0.0)
            responses_map[item["id"]] = score
            evaluation_rows.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "phase_id": item["phase_id"],
                    "phase_name": item["phase_name"],
                    "weight": item["weight"],
                    "value": score,
                }
            )
        try:
            timestamp = save_ebct_evaluation(project_id, evaluation_rows)
            st.session_state["ebct_panel_map"] = responses_map
            st.session_state["ebct_last_eval_timestamp"] = timestamp
            st.session_state["show_save_message"] = True
            panel_map = responses_map
            last_eval_timestamp = timestamp
            history_df = get_ebct_history(project_id)
            last_eval_map = responses_map
            # No rerun, solo mostrar mensaje en la siguiente renderización
        except Exception as error:
            st.session_state["show_error_message"] = str(error)
    
    # Mostrar mensajes después del formulario (sin causar saltos)
    if st.session_state.get('show_save_message', False):
        st.success("✅ Evaluación EBCT guardada correctamente.")
        st.session_state.show_save_message = False
    
    if st.session_state.get('show_error_message'):
        st.error(f"❌ Error al guardar: {st.session_state.show_error_message}")
        del st.session_state.show_error_message
    
    # Lógica para generar semáforo
    if generate_semaforo:
        # Construir mapa de respuestas desde st.session_state
        current_map = {}
        for item in EBCT_CHARACTERISTICS:
            key = f"ebct_resp_{item['id']}"
            respuesta = st.session_state.get(key, OPTION_NO)
            # Convertir respuesta a score numérico (0.0, 0.5, 1.0)
            score_val = OPTION_SCORES.get(respuesta, 0.0)
            current_map[item["id"]] = score_val

        sem_df = compute_semaforo(current_map)
        
        # Guardar en session_state para persistir después de descargas
        st.session_state.semaforo_df = sem_df
        st.session_state.semaforo_generated = True
        # No hacer rerun, se mostrará automáticamente abajo

    # Mostrar semáforo si fue generado (persiste después de descargas)
    if st.session_state.get('semaforo_generated', False) and 'semaforo_df' in st.session_state:
        sem_df = st.session_state.semaforo_df
        
        # Mostrar semáforo
        st.markdown("---")
        st.markdown("### 🚦 Semáforo de Evaluación EBCT")
        
        # Calcular métricas
        total_items = len(sem_df)
        achieved = (sem_df["Score"] * sem_df["Peso"]).sum()
        total_weight = sem_df["Peso"].sum() if total_items else 0.0
        pct = (achieved / total_weight * 100) if total_weight else 0.0
        
        # Tarjeta de KPIs Generales con diseño moderno
        kpi_card_html = f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 24px;
            margin: 20px 0;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
        ">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                <div style="text-align: center; color: white;">
                    <div style="font-size: 2.5em; font-weight: 700; margin-bottom: 8px;">📋</div>
                    <div style="font-size: 2.2em; font-weight: 800; margin-bottom: 4px;">{total_items}</div>
                    <div style="font-size: 0.9em; opacity: 0.95; font-weight: 500;">Características evaluadas</div>
                </div>
                <div style="text-align: center; color: white;">
                    <div style="font-size: 2.5em; font-weight: 700; margin-bottom: 8px;">⚖️</div>
                    <div style="font-size: 2.2em; font-weight: 800; margin-bottom: 4px;">{achieved:.2f}</div>
                    <div style="font-size: 0.9em; opacity: 0.95; font-weight: 500;">Peso logrado</div>
                </div>
                <div style="text-align: center; color: white;">
                    <div style="font-size: 2.5em; font-weight: 700; margin-bottom: 8px;">✅</div>
                    <div style="font-size: 2.2em; font-weight: 800; margin-bottom: 4px;">{pct:.1f}%</div>
                    <div style="font-size: 0.9em; opacity: 0.95; font-weight: 500;">Cumplimiento global</div>
                </div>
            </div>
        </div>
        """
        st.markdown(kpi_card_html, unsafe_allow_html=True)

        # Definir orden de fases
        phase_order = {
            "Fase Incipiente": 1,
            "Fase Validación y PI": 2,
            "Fase Preparación para Mercado": 3,
            "Fase Internacionalización": 4,
        }
        ordered_phases = sorted(sem_df["Fase"].unique(), key=lambda x: phase_order.get(x, 999))

        # Tarjetas de cumplimiento por fase con diseño moderno
        st.markdown("#### 📊 Cumplimiento por Fase")
        
        # Definir las 4 fases y sus colores
        all_phases = [
            "Fase Incipiente",
            "Fase Validación y PI",
            "Fase Preparación para Mercado",
            "Fase Internacionalización"
        ]
        
        fase_colors_gradient = {
            "Fase Incipiente": {"from": "#5e35b1", "to": "#7e57c2", "icon": "🟣"},
            "Fase Validación y PI": {"from": "#2e7d32", "to": "#43a047", "icon": "🟢"},
            "Fase Preparación para Mercado": {"from": "#1565c0", "to": "#1976d2", "icon": "🔵"},
            "Fase Internacionalización": {"from": "#f57f17", "to": "#fbc02d", "icon": "🟡"}
        }
        
        # Crear 4 columnas para las tarjetas (una al lado de otra)
        cols_fase = st.columns(4)
        
        for idx, fase in enumerate(all_phases):
            fase_data = sem_df[sem_df["Fase"] == fase]
            if not fase_data.empty:
                fase_achieved = (fase_data["Score"] * fase_data["Peso"]).sum()
                fase_total_weight = fase_data["Peso"].sum()
                fase_pct = (fase_achieved / fase_total_weight * 100) if fase_total_weight else 0.0
            else:
                fase_pct = 0.0
            
            # Nombre corto de la fase
            fase_short = fase.replace("Fase ", "")
            colors = fase_colors_gradient.get(fase)
            
            # Todos los textos en blanco para un look limpio y profesional
            text_color = "#ffffff"
            
            # Renderizar tarjeta en su columna correspondiente
            with cols_fase[idx]:
                card_html = f"""
                <div style="background: linear-gradient(135deg, {colors['from']} 0%, {colors['to']} 100%); border-radius: 12px; padding: 30px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s ease; cursor: default; height: 130px; display: flex; flex-direction: column; align-items: center; justify-content: center;" onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.25)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'">
                    <div style="text-align: center; color: {text_color}; width: 100%;">
                        <div style="font-size: 3em; font-weight: 800; line-height: 1; margin-bottom: 12px;">{fase_pct:.1f}%</div>
                        <div style="font-size: 0.9em; font-weight: 600; opacity: 0.95; letter-spacing: 0.5px; text-transform: uppercase;">{fase_short}</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

        # Mapa Semáforo Horizontal - Vista consolidada de las 4 fases
        st.markdown("#### Mapa Semáforo EBCT - Vista Horizontal")
        st.caption("Las 4 fases se muestran en horizontal (tipo matriz). Cada celda muestra el ID de la característica con su color según el estado.")
        
        # Definir las 4 fases que siempre deben mostrarse
        all_phases = [
            "Fase Incipiente",
            "Fase Validación y PI",
            "Fase Preparación para Mercado",
            "Fase Internacionalización"
        ]
        
        # Colores por fase
        fase_colors = {
            "Fase Incipiente": "#673AB7",
            "Fase Validación y PI": "#4CAF50",
            "Fase Preparación para Mercado": "#2196F3",
            "Fase Internacionalización": "#FFC107"
        }
        
        # Construir el HTML completo del semáforo horizontal
        semaforo_html = """<style>
.semaforo-matriz {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 2rem 0;
    width: 100%;
}

.fase-box {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-top: 5px solid;
    min-height: 200px;
}

.fase-titulo {
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-align: center;
    padding: 0.6rem;
    border-radius: 8px;
    color: white;
}

.ids-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
    gap: 0.6rem;
    min-height: 100px;
}

.id-box {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.id-box:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    z-index: 100;
}

.id-box.verde {
    background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
}

.id-box.amarillo {
    background: linear-gradient(135deg, #f9a825 0%, #fdd835 100%);
    color: #333;
}

.id-box.rojo {
    background: linear-gradient(135deg, #c62828 0%, #ef5350 100%);
}

.tooltip-info {
    display: none;
    position: fixed;
    bottom: auto;
    left: auto;
    right: auto;
    background: linear-gradient(135deg, rgba(0,0,0,0.95), rgba(27,94,32,0.95));
    color: white;
    padding: 14px 18px;
    border-radius: 10px;
    border: 2px solid #2e7d32;
    box-shadow: 0 8px 24px rgba(0,0,0,0.7);
    white-space: normal;
    z-index: 1000;
    font-size: 13px;
    line-height: 1.6;
    text-align: left;
    width: 320px;
    max-width: 90vw;
    pointer-events: none;
}

.id-box {
    overflow: visible;
}

.id-box:hover .tooltip-info {
    display: block;
}

/* Posicionar tooltip arriba y centrado por defecto */
.fase-box:nth-child(1) .tooltip-info,
.fase-box:nth-child(2) .tooltip-info,
.fase-box:nth-child(3) .tooltip-info,
.fase-box:nth-child(4) .tooltip-info {
    position: absolute;
    bottom: 110%;
    left: 50%;
    transform: translateX(-50%);
}

/* Para la primera columna (izquierda): alinear a la izquierda */
.fase-box:nth-child(1) .tooltip-info {
    left: 0;
    transform: translateX(0);
}

/* Para la última columna (derecha): alinear a la derecha */
.fase-box:nth-child(4) .tooltip-info {
    left: auto;
    right: 0;
    transform: translateX(0);
}

.tooltip-info strong {
    color: #81c784;
    display: block;
    margin-top: 6px;
}

.empty-fase {
    text-align: center;
    color: #999;
    font-size: 0.85rem;
    padding: 2rem 0.5rem;
    font-style: italic;
}

@media (max-width: 1200px) {
    .semaforo-matriz {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .semaforo-matriz {
        grid-template-columns: 1fr;
    }
}
</style>

<div class='semaforo-matriz'>"""
        
        # Generar cada columna de fase
        for fase in all_phases:
            # Filtrar características de esta fase
            fase_data = sem_df[sem_df["Fase"] == fase].sort_values("id")
            fase_color = fase_colors.get(fase, "#666666")
            
            semaforo_html += f"""
<div class='fase-box' style='border-top-color: {fase_color};'>
    <div class='fase-titulo' style='background: {fase_color};'>{fase}</div>
    <div class='ids-container'>"""
            
            if fase_data.empty:
                semaforo_html += """
    <div class='empty-fase' style='grid-column: 1/-1;'>
        Sin características<br>evaluadas
    </div>"""
            else:
                # Agregar cada característica como una celda con ID
                for _, row in fase_data.iterrows():
                    char_id = row["id"]
                    estado = row["EstadoSemaforo"]
                    nombre = row["Característica"]
                    dims = row["Dimensiones"]
                    score = row["Score"]
                    peso = row["Peso"]
                    
                    # Determinar color según estado
                    if "Verde" in estado or "🟢" in estado:
                        color_class = "verde"
                    elif "Amarillo" in estado or "🟡" in estado:
                        color_class = "amarillo"
                    elif "Rojo" in estado or "🔴" in estado:
                        color_class = "rojo"
                    else:
                        # Fallback por si acaso
                        color_class = "amarillo"
                    
                    # Crear tooltip con información
                    tooltip_html = f"""<strong>ID:</strong> {char_id}<br>
<strong>Característica:</strong> {escape(nombre)}<br>
<strong>Dimensiones:</strong><br>{escape(dims).replace(' | ', '<br>• ')}<br>
<strong>Estado:</strong> {estado}<br>
<strong>Score:</strong> {score:.1f} / Peso: {peso}"""
                    
                    semaforo_html += f"""
    <div class='id-box {color_class}'>
        {char_id}
        <span class='tooltip-info'>{tooltip_html}</span>
    </div>"""
            
            semaforo_html += """
    </div>
</div>"""
        
        semaforo_html += "</div>"
        
        # Renderizar el semáforo
        st.markdown(semaforo_html, unsafe_allow_html=True)

        # Visualizaciones: Radar y Heatmap
        col_radar, col_heat = st.columns(2)

        with col_radar:
            st.markdown("#### Radar por Fase")
            # Preparar datos por fase para el radar (y ordenar según ordered_phases)
            radar_df = sem_df.groupby("Fase").agg({
                "Score": lambda x: (x * sem_df.loc[x.index, "Peso"]).sum() / sem_df.loc[x.index, "Peso"].sum()
            }).reset_index()
            # Reordenar radar_df según ordered_phases
            radar_df = radar_df.set_index("Fase").reindex(ordered_phases).reset_index()
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_df["Score"] * 100,
                theta=radar_df["Fase"],
                fill="toself",
                name="Cumplimiento",
                fillcolor="rgba(31, 107, 54, 0.35)",
                line=dict(color="rgb(31, 107, 54)"),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        ticksuffix="%",
                        gridcolor="rgba(0,0,0,0.1)",
                        showline=False,
                    ),
                    bgcolor="rgba(255,255,255,0.95)",
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_heat:
            st.markdown("#### Heatmap de Cumplimiento")
            # Preparar matriz para heatmap y reordenar filas según ordered_phases
            heat_df = sem_df.pivot_table(
                values="Score",
                index="Fase",
                columns="Característica",
                aggfunc="first"
            )
            heat_df = heat_df.reindex(ordered_phases)
            
            # Reemplazar NaN con None para que no se muestren en el heatmap
            import numpy as np
            heat_values = heat_df.values.copy()
            heat_values = np.where(np.isnan(heat_values), None, heat_values)
            
            # Crear matriz de hover text que coincida con el heatmap
            hover_matrix = []
            for fase in heat_df.index:
                hover_row = []
                for caracteristica in heat_df.columns:
                    val = heat_df.loc[fase, caracteristica]
                    if pd.notna(val):
                        # Buscar info de la característica
                        matching = sem_df[(sem_df['Fase'] == fase) & (sem_df['Característica'] == caracteristica)]
                        if not matching.empty:
                            row = matching.iloc[0]
                            hover_row.append(
                                f"<b>{caracteristica}</b><br>" +
                                f"Fase: {fase}<br>" +
                                f"Dimensiones: {row['Dimensiones']}<br>" +
                                f"Estado: {row['EstadoSemaforo']}<br>" +
                                f"Score: {val:.2f}"
                            )
                        else:
                            hover_row.append(f"{caracteristica}<br>Score: {val:.2f}")
                    else:
                        hover_row.append("Sin datos")
                hover_matrix.append(hover_row)

            fig_heat = go.Figure(data=go.Heatmap(
                z=heat_values,
                x=heat_df.columns,
                y=heat_df.index,
                text=hover_matrix,
                colorscale=[
                    [0, "rgb(239, 83, 80)"],      # Rojo claro para 0 (más visible sobre fondo blanco)
                    [0.39, "rgb(255, 138, 128)"], # Rojo suave para valores bajos (< 0.4)
                    [0.4, "rgb(255, 193, 7)"],    # Amarillo empieza en 0.4
                    [0.65, "rgb(255, 215, 0)"],   # Amarillo medio
                    [0.89, "rgb(255, 241, 118)"], # Amarillo claro antes del verde
                    [0.9, "rgb(102, 187, 106)"],  # Verde empieza en 0.9
                    [1, "rgb(46, 125, 50)"]       # Verde oscuro para 1
                ],
                hoverongaps=True,
                connectgaps=False,
                showscale=True,
                hoverinfo='text',
                colorbar=dict(
                    title="Score",
                    tickmode="array",
                    ticktext=["🔴 Rojo<br>< 0.4", "🟡 Amarillo<br>0.4 - 0.89", "🟢 Verde<br>≥ 0.9"],
                    tickvals=[0.2, 0.65, 0.95],
                    ticks="outside",
                    len=0.9
                ),
                zmin=0,
                zmax=1
            ))
            fig_heat.update_layout(
                template="plotly_white",
                margin=dict(l=40, r=40, t=20, b=60),
                height=350,
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="black"),
                xaxis=dict(
                    tickangle=45,
                    showgrid=True,
                    gridcolor="rgba(200,200,200,0.3)",
                    linecolor="rgba(0,0,0,0.1)",
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(200,200,200,0.3)",
                    linecolor="rgba(0,0,0,0.1)",
                )
            )
            st.plotly_chart(fig_heat, use_container_width=True, theme=None)

        # Tabla detallada con diseño innovador
        st.markdown("---")
        st.markdown("#### 📋 Detalle de Evaluación por Característica")
        st.caption("Vista completa de las 34 características EBCT con sus dimensiones, pesos y estados")
        
        # Preparar DataFrame para mostrar
        display_df = sem_df.copy()
        
        # Reordenar según fases
        display_df["Fase"] = pd.Categorical(display_df["Fase"], categories=ordered_phases, ordered=True)
        display_df = display_df.sort_values(["Fase", "id"])
        
        # Seleccionar y reordenar columnas para mejor presentación
        display_df_final = display_df[["id", "Fase", "Característica", "Dimensiones", "EstadoSemaforo", "Score", "Peso"]].copy()
        display_df_final.columns = ["ID", "Fase", "Característica", "Dimensiones", "Estado", "Score", "Peso"]
        
        # Aplicar formato condicional con HTML personalizado
        def format_estado(val):
            if "Verde" in val or "🟢" in val:
                return f'<div style="background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 6px 12px; border-radius: 6px; text-align: center; font-weight: 600;">{val}</div>'
            elif "Amarillo" in val or "🟡" in val:
                return f'<div style="background: linear-gradient(135deg, #f9a825, #fdd835); color: #333; padding: 6px 12px; border-radius: 6px; text-align: center; font-weight: 600;">{val}</div>'
            elif "Rojo" in val or "🔴" in val:
                return f'<div style="background: linear-gradient(135deg, #c62828, #ef5350); color: white; padding: 6px 12px; border-radius: 6px; text-align: center; font-weight: 600;">{val}</div>'
            return val
        
        def format_score(val):
            if val >= 0.9:
                color = "#2e7d32"
            elif val >= 0.4:
                color = "#f9a825"
            else:
                color = "#c62828"
            return f'<div style="color: {color}; font-weight: 700; font-size: 1.1em;">{val:.2f}</div>'
        
        def format_id(val):
            return f'<div style="background: #1976d2; color: white; padding: 4px 8px; border-radius: 4px; text-align: center; font-weight: 700;">{val}</div>'
        
        # Convertir a HTML con estilos
        html_table = '<div style="overflow-x: auto; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
        html_table += '<table style="width: 100%; border-collapse: collapse; background: white;">'
        
        # Encabezado con estilo
        html_table += '<thead><tr style="background: linear-gradient(135deg, #1976d2, #2196f3); color: white;">'
        for col in display_df_final.columns:
            html_table += f'<th style="padding: 12px; text-align: left; font-weight: 600; border-bottom: 3px solid #0d47a1;">{col}</th>'
        html_table += '</tr></thead>'
        
        # Cuerpo de la tabla con filas alternadas
        html_table += '<tbody>'
        for idx, row in display_df_final.iterrows():
            bg_color = "#f8f9fa" if idx % 2 == 0 else "#ffffff"
            html_table += f'<tr style="background: {bg_color}; transition: all 0.2s ease;" onmouseover="this.style.background=\'#e3f2fd\'" onmouseout="this.style.background=\'{bg_color}\'">'
            
            # ID
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">{format_id(row["ID"])}</td>'
            
            # Fase
            fase_color = fase_colors.get(row["Fase"], "#666666")
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0;"><span style="color: {fase_color}; font-weight: 600;">●</span> {row["Fase"].replace("Fase ", "")}</td>'
            
            # Característica
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0; max-width: 300px;"><div style="font-weight: 500;">{escape(row["Característica"])}</div></td>'
            
            # Dimensiones - con diseño compacto
            dims_html = row["Dimensiones"].replace(" | ", "<br>• ")
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0; font-size: 0.85em; color: #666;">• {dims_html}</td>'
            
            # Estado
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">{format_estado(row["Estado"])}</td>'
            
            # Score
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: center;">{format_score(row["Score"])}</td>'
            
            # Peso
            html_table += f'<td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: 600;">{row["Peso"]}</td>'
            
            html_table += '</tr>'
        
        html_table += '</tbody></table></div>'
        
        # Renderizar tabla HTML
        st.markdown(html_table, unsafe_allow_html=True)
        
        # Botón de descarga como Excel
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
            display_df_final.to_excel(writer, sheet_name='Evaluación EBCT', index=False)
            
            # Opcional: ajustar anchos de columnas
            worksheet = writer.sheets['Evaluación EBCT']
            worksheet.column_dimensions['A'].width = 8   # ID
            worksheet.column_dimensions['B'].width = 25  # Fase
            worksheet.column_dimensions['C'].width = 40  # Característica
            worksheet.column_dimensions['D'].width = 50  # Dimensiones
            worksheet.column_dimensions['E'].width = 18  # Estado
            worksheet.column_dimensions['F'].width = 10  # Score
            worksheet.column_dimensions['G'].width = 10  # Peso
        
        excel_data = excel_buf.getvalue()
        
        st.download_button(
            "📥 Descargar tabla detallada (Excel)",
            excel_data,
            file_name=f"evaluacion_ebct_detallada_proyecto_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Descarga la tabla completa con todas las características evaluadas",
            key=f"download_excel_detalle_{project_id}"
        )

    st.markdown("</div>", unsafe_allow_html=True)
