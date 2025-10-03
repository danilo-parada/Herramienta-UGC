
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Plataforma EBCT", page_icon=":bar_chart:", layout="wide")

BENEFITS = [
    "Mostrar de forma visual e interactiva la hoja de ruta",
    "Facilitar la identificacion de financiamiento, programas y aliados",
    "Reducir la incertidumbre y mejorar la gestion estrategica",
]

PHASES = [
    {
        "title": "Fase 0",
        "subtitle": "Portafolio y filtro inicial",
        "summary": "Registrar iniciativas en el portafolio maestro con datos clave y filtros de madurez",
        "detail": "Consolida informacion (impacto, estado, responsables, fechas) y realiza un primer filtro para definir avance.",
    },
    {
        "title": "Fase 1",
        "subtitle": "IRL (Radiografia)",
        "summary": "Evaluar seis dimensiones (CRL, BRL, TRL, IPRL, TmRL, FRL) y obtener la radiografia del proyecto",
        "detail": "Aplica la calculadora de madurez para cliente, negocio, tecnologia, PI, equipo y financiamiento con evidencias trazables.",
    },
    {
        "title": "Fase 2",
        "subtitle": "EBCT",
        "summary": "Analizar el proyecto segun la trayectoria EBCT (Incipiente, Validacion/PI, Mercado, Comercializacion)",
        "detail": "Revisa subcaracteristicas EBCT, identifica brechas y prepara recomendaciones para mercado y comercializacion.",
    },
    {
        "title": "Fase 3",
        "subtitle": "Diagnostico",
        "summary": "Definir requerimientos de recursos humanos, tecnologia y financiamiento",
        "detail": "Elabora carta Gantt, lista de recursos y planifica reuniones de seguimiento para cerrar brechas.",
    },
    {
        "title": "Fase 4",
        "subtitle": "Panel de indicadores",
        "summary": "Monitorear el portafolio y el desempeno de cada proyecto",
        "detail": "Integra datos en paneles individuales y generales para apoyar decisiones estrategicas.",
    },
]

BLOQUES = [
    "La plataforma filtra proyectos que avanzaran a la evaluacion de madurez.",
    "Cada dimension tiene nueve niveles para visualizar progreso.",
    "Un experto valida evidencias y obtiene un diagnostico cualitativo.",
    "Elaboracion de cronograma, recursos y reuniones de seguimiento.",
]

ROLES = [
    {"label": "Portafolio Maestro", "subtitle": "Gerencia I+D+I INFOR", "color": "#167C82"},
    {"label": "Responsable Innovacion", "subtitle": "Investigadores INFOR", "color": "#167C82"},
    {"label": "Equipo", "subtitle": "UGC-INFOR", "color": "#35B6BF"},
    {"label": "UGC / UdT", "subtitle": "Gerencia I+D+I INFOR", "color": "#35B6BF"},
]

st.markdown(
    """
<style>
body { background-color: #F4F6F8; }
h1, h2, h3 { font-weight: 700; letter-spacing: 0.2px; }
.benefits { background: #ffffff; border-radius: 12px; padding: 1.2rem; border: 1px solid #d7e0e5; }
.benefits ul { margin: 0; padding-left: 1.2rem; }
.phase-card { text-align: center; padding: 0 0.5rem; }
.phase-circle {
    width: 200px; height: 200px; margin: 0 auto 0.8rem auto; border-radius: 50%;
    background: linear-gradient(145deg, #1c939d, #15717a);
    color: #ffffff; display: flex; flex-direction: column; justify-content: center; align-items: center;
    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
}
.phase-title { font-size: 1rem; font-weight: 700; text-transform: uppercase; }
.phase-subtitle { font-size: 0.9rem; font-weight: 600; margin-top: 0.2rem; }
.phase-summary { font-size: 0.85rem; color: #0f3d44; min-height: 70px; }
.arrow-banner {
    margin: 2rem 0 1.5rem 0; position: relative; background: #B08D57; color: #ffffff;
    text-align: center; padding: 0.9rem 1.5rem; font-weight: 700; letter-spacing: 1px;
}
.arrow-banner:after {
    content: ""; position: absolute; top: 0; right: -60px; width: 0; height: 0;
    border-top: 30px solid transparent; border-bottom: 30px solid transparent; border-left: 60px solid #B08D57;
}
.block-card {
    background: #ffffff; border: 1px solid #E0E5EA; border-radius: 12px;
    padding: 1rem; min-height: 140px; box-shadow: 0 6px 14px rgba(15,61,68,0.08);
}
.roles-line { display: flex; justify-content: space-between; align-items: center; gap: 1.2rem;
    margin: 2rem 0 1rem 0; padding: 1rem 1.5rem; background: #ffffff; border-radius: 20px;
    border: 1px solid #d7e0e5; box-shadow: 0 6px 16px rgba(15,61,68,0.08); }
.role-item { text-align: center; flex: 1; font-size: 0.95rem; }
.role-dot { width: 22px; height: 22px; border-radius: 50%; margin: 0 auto 0.6rem auto; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("## PLATAFORMA DE GESTION DE INNOVACIONES INFOR")
st.markdown("Describe las fases del proceso de gestion de proyectos de la UGC")

header_cols = st.columns([2, 1])
with header_cols[1]:
    st.markdown("### Beneficios")
    st.markdown("<div class='benefits'><ul>" + "".join(f"<li>{item}</li>" for item in BENEFITS) + "</ul></div>", unsafe_allow_html=True)

st.divider()

phase_cols = st.columns(len(PHASES))
for col, phase in zip(phase_cols, PHASES):
    with col:
        st.markdown(
            f"""
<div class='phase-card'>
  <div class='phase-circle'>
    <div class='phase-title'>{phase['title']}</div>
    <div class='phase-subtitle'>{phase['subtitle']}</div>
  </div>
  <div class='phase-summary'>{phase['summary']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.expander("Detalle"):
            st.write(phase["detail"])

st.markdown("<div class='arrow-banner'>HOJA DE RUTA PROYECTO DESDE LA I+D A LA COMERCIALIZACION</div>", unsafe_allow_html=True)

block_cols = st.columns(4)
for col, text in zip(block_cols, BLOQUES):
    with col:
        st.markdown(f"<div class='block-card'>{text}</div>", unsafe_allow_html=True)

st.divider()

roles_html = "<div class='roles-line'>"
for role in ROLES:
    roles_html += (
        f"<div class='role-item'><div class='role-dot' style='background:{role['color']}'></div>"
        f"<strong>{role['label']}</strong><br><span>{role['subtitle']}</span></div>"
    )
roles_html += "</div>"
st.markdown(roles_html, unsafe_allow_html=True)
fase0_page = next(Path("pages").glob("02_*_Fase_0_Portafolio.py"), None)
if fase0_page:
    st.markdown("<div style='text-align:center; margin-top:1rem;'>", unsafe_allow_html=True)
    if st.button("Ir a Fase 0", type="primary"):
        st.switch_page(str(fase0_page))
    st.markdown("</div>", unsafe_allow_html=True)
