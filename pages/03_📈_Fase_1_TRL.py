import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path

from core import db, utils, trl
from core.db_trl import save_trl_result, get_trl_history
from core.theme import load_theme

IRL_DIMENSIONS = [
    ("CRL", 6),
    ("BRL", 5),
    ("TRL", 4),
    ("IPRL", 5),
    ("TmRL", 6),
    ("FRL", 5),
]

CRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Hipótesis especulativa sobre una posible necesidad en el mercado.",
        "preguntas": [
            "¿Tiene alguna hipótesis sobre un problema o necesidad que podría existir en el mercado?",
            "¿Ha identificado quiénes podrían ser sus posibles clientes, aunque sea de manera especulativa?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Familiarización inicial con el mercado y necesidades más específicas detectadas.",
        "preguntas": [
            "¿Ha realizado alguna investigación secundaria o revisión de mercado para entender problemas del cliente?",
            "¿Tiene una descripción más clara y específica de las necesidades o problemas detectados?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Primer feedback de mercado y validación preliminar de necesidades.",
        "preguntas": [
            "¿Ha iniciado contactos directos con posibles usuarios o expertos del mercado para obtener retroalimentación?",
            "¿Ha comenzado a desarrollar una hipótesis más clara sobre los segmentos de clientes y sus problemas?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Confirmación del problema con varios usuarios y segmentación inicial.",
        "preguntas": [
            "¿Ha confirmado el problema o necesidad con varios clientes o usuarios reales?",
            "¿Ha definido una hipótesis de producto basada en el feedback recibido de los usuarios?",
            "¿Tiene segmentación inicial de clientes en función del problema identificado?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "Interés establecido por parte de usuarios y comprensión más profunda del mercado.",
        "preguntas": [
            "¿Cuenta con evidencia de interés concreto por parte de clientes o usuarios hacia su solución?",
            "¿Ha establecido relaciones con potenciales clientes o aliados que retroalimentan su propuesta de valor?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "Beneficios de la solución confirmados a través de pruebas o asociaciones iniciales.",
        "preguntas": [
            "¿Ha realizado pruebas del producto o solución con clientes que validen sus beneficios?",
            "¿Ha iniciado procesos de venta o pilotos con clientes reales o aliados estratégicos?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "Clientes involucrados en pruebas extendidas o primeras ventas/test comerciales.",
        "preguntas": [
            "¿Tiene acuerdos o primeras ventas del producto (aunque sea versión de prueba)?",
            "¿Los clientes han participado activamente en validaciones o pruebas extendidas del producto?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Ventas iniciales y preparación para ventas estructuradas y escalables.",
        "preguntas": [
            "¿Ha vendido sus primeros productos y validado la disposición de pago de un porcentaje relevante de clientes?",
            "¿Cuenta con una organización comercial mínima (CRM, procesos de venta, canales definidos)?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "Adopción consolidada y ventas repetibles a múltiples clientes reales.",
        "preguntas": [
            "¿Está realizando ventas escalables y repetibles con múltiples clientes?",
            "¿Su empresa está enfocada en ejecutar un proceso de crecimiento comercial con foco en la demanda de clientes?",
        ],
    },
]

def _init_irl_state():
    if "irl_scores" not in st.session_state:
        st.session_state["irl_scores"] = {dimension: default for dimension, default in IRL_DIMENSIONS}
    if "irl_answers" not in st.session_state:
        st.session_state["irl_answers"] = {}


def _compute_consecutive_level(dimension: str, levels: list[dict]) -> int:
    reached_level = 0
    for level_data in levels:
        preguntas = level_data.get("preguntas", [])
        nivel_validado = True
        for idx, _ in enumerate(preguntas, start=1):
            answer_key = f"irl_{dimension}_L{level_data['nivel']}_Q{idx}"
            if st.session_state.get(answer_key, "FALSO") != "VERDADERO":
                nivel_validado = False
                break
        if nivel_validado:
            reached_level = level_data["nivel"]
        else:
            break
    return reached_level


def _render_crl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez del cliente (CRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in CRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_CRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("CRL", CRL_LEVELS)
    st.session_state["irl_scores"]["CRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: CRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel CRL.")


def _render_placeholder_tab(dimension: str):
    _init_irl_state()
    score_key = f"irl_manual_{dimension}"
    default_value = int(st.session_state["irl_scores"].get(dimension, 0))
    st.info("Define temporalmente el nivel de madurez mientras se agregan las preguntas específicas.")
    nivel = st.slider(
        f"Selecciona el nivel de {dimension}",
        min_value=0,
        max_value=9,
        value=default_value,
        key=score_key,
    )
    st.session_state["irl_scores"][dimension] = nivel


st.set_page_config(page_title="Fase 1 - Evaluacion TRL", page_icon="🌲", layout="wide")
load_theme()

st.markdown(
    """
<style>
.page-intro {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
    gap: 2.4rem;
    padding: 2.3rem 2.6rem;
    border-radius: 30px;
    background: linear-gradient(145deg, rgba(18, 48, 29, 0.94), rgba(111, 75, 44, 0.88));
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

.metric-ribbon {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 1.1rem;
    margin: 1.4rem 0 2.1rem;
}

.metric-ribbon__item {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.3rem 1.4rem;
    border: 1px solid rgba(var(--shadow-color), 0.12);
    box-shadow: 0 20px 42px rgba(var(--shadow-color), 0.16);
    position: relative;
    overflow: hidden;
}

.metric-ribbon__item:after {
    content: "";
    position: absolute;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(37, 87, 52, 0.12);
    top: -40px;
    right: -50px;
}

.metric-ribbon__value {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--forest-700);
    position: relative;
}

.metric-ribbon__label {
    display: block;
    margin-top: 0.4rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.55px;
    text-transform: uppercase;
    color: var(--text-500);
}

.section-shell {
    background: #ffffff;
    border-radius: 24px;
    padding: 1.6rem 1.8rem;
    border: 1px solid rgba(var(--shadow-color), 0.12);
    box-shadow: 0 24px 48px rgba(var(--shadow-color), 0.16);
    margin-bottom: 2.3rem;
}

.section-shell--split {
    padding: 1.6rem 1.2rem 1.9rem;
}

.section-shell h3, .section-shell h4 {
    margin-top: 0;
}

.threshold-band {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0.6rem 0 1rem;
}

.threshold-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 1rem;
    border-radius: 16px;
    background: rgba(var(--forest-500), 0.16);
    color: var(--text-700);
    font-weight: 600;
    border: 1px solid rgba(var(--forest-500), 0.22);
}

.threshold-chip strong {
    font-size: 1rem;
    color: var(--forest-700);
}

.history-caption {
    color: var(--text-500);
    margin-bottom: 0.8rem;
}

@media (max-width: 992px) {
    .page-intro {
        grid-template-columns: 1fr;
    }

    .back-band {
        justify-content: center;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-intro">
        <div>
            <span class="badge-soft">Fase 1 · IRL / TRL</span>
            <h1>Evaluacion estrategica de madurez tecnologica</h1>
            <p>
                Priorizamos proyectos del portafolio maestro para registrar evidencias por dimension, estimar el TRL e impulsar el
                cierre de brechas con una mirada integral entre cliente, negocio y tecnologia.
            </p>
        </div>
        <div class="page-intro__aside">
            <div class="intro-stat">
                <strong>Objetivo</strong>
                <p>Seleccionar iniciativas clave y capturar sus niveles IRL, alineando evidencia y responsables.</p>
            </div>
            <div class="intro-stat">
                <strong>Resultado</strong>
                <p>Perfil comparativo IRL con historial descargable y focos para la ruta comercial EBCT.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

fase0_page = next(Path("pages").glob("02_*_Fase_0_Portafolio.py"), None)
if fase0_page:
    st.markdown("<div class='back-band'>", unsafe_allow_html=True)
    if st.button("Volver a Fase 0", type="primary"):
        st.switch_page(str(fase0_page))
    st.markdown("</div>", unsafe_allow_html=True)

payload = st.session_state.get('fase1_payload')
fase1_ready = st.session_state.get('fase1_ready', False)

if not payload or not fase1_ready:
    st.warning('Calcula el ranking de candidatos en Fase 0 y usa el boton "Ir a Fase 1" para continuar.')
    if fase0_page:
        if st.button('Ir a Fase 0', key='btn_ir_fase0_desde_fase1'):
            st.switch_page(str(fase0_page))
    st.stop()

ranking_df = payload['ranking'].copy().reset_index(drop=True)
if ranking_df.empty:
    st.warning('El ranking recibido esta vacio. Recalcula la priorizacion en Fase 0.')
    if fase0_page:
        if st.button('Recalcular en Fase 0', key='btn_recalcular_fase0'):
            st.switch_page(str(fase0_page))
    st.stop()

metrics_cards = payload.get('metrics_cards', [])
umbrales = payload.get('umbrales', {})

if metrics_cards:
    metrics_html = "<div class='metric-ribbon'>"
    for label, value in metrics_cards:
        metrics_html += (
            "<div class='metric-ribbon__item'>"
            f"<span class='metric-ribbon__value'>{value}</span>"
            f"<span class='metric-ribbon__label'>{label}</span>"
            "</div>"
        )
    metrics_html += "</div>"
    st.markdown(metrics_html, unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown('#### Ranking de candidatos priorizados')
    if umbrales:
        thresholds = "".join(
            f"<span class='threshold-chip'><strong>{valor}</strong>{nombre}</span>" for nombre, valor in umbrales.items()
        )
        st.markdown(f"<div class='threshold-band'>{thresholds}</div>", unsafe_allow_html=True)

    ranking_display = ranking_df.copy()
    styled_ranking = ranking_display.style.format({'evaluacion_calculada': '{:.1f}'})
    styled_ranking = styled_ranking.apply(
        lambda row: [
            'background-color: rgba(37, 87, 52, 0.18); color: #1f2a1d; font-weight:600' if row.name < 3 else ''
            for _ in row
        ],
        axis=1,
    )
    st.dataframe(styled_ranking, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

ranking_keys = ranking_df[['id_innovacion', 'ranking']].copy()
ranking_keys['id_str'] = ranking_keys['id_innovacion'].astype(str)

df_port = utils.normalize_df(db.fetch_df())
df_port['id_str'] = df_port['id_innovacion'].astype(str)
df_port = df_port[df_port['id_str'].isin(ranking_keys['id_str'])].copy()
if df_port.empty:
    st.warning('Los proyectos del ranking ya no estan disponibles en el portafolio maestro. Recalcula la priorizacion en Fase 0.')
    if fase0_page:
        if st.button('Volver a Fase 0', key='btn_volver_recalcular'):
            st.switch_page(str(fase0_page))
    st.stop()

order_map = dict(zip(ranking_keys['id_str'], ranking_keys['ranking']))
df_port['orden_ranking'] = df_port['id_str'].map(order_map)
df_port = df_port.sort_values('orden_ranking').reset_index(drop=True)
df_port = df_port.drop(columns=['id_str', 'orden_ranking'], errors='ignore')



def parse_project_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        st.error('No se puede registrar la evaluacion porque el identificador del proyecto no es numerico. Revisa la Fase 0.')
        st.stop()


def fmt_opt(identificador: int) -> str:
    fila = df_port.loc[df_port["id_innovacion"] == identificador]
    if fila.empty:
        return str(identificador)
    return f"{identificador} - {fila['nombre_innovacion'].values[0]}"


with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown("### Selecciona un proyecto del portafolio maestro")
    ids = df_port["id_innovacion"].tolist()
    seleccion = st.selectbox("Proyecto", ids, format_func=fmt_opt)
    st.markdown("</div>", unsafe_allow_html=True)


project_id = parse_project_id(seleccion)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown("### Dimensiones y evidencias")
    df_resp = trl.esquema_respuestas()

    df_resp = st.data_editor(
        df_resp,
        num_rows="fixed",
        hide_index=True,
        use_container_width=True,
        column_config={
            "dimension": st.column_config.TextColumn("Dimension", disabled=True),
            "nivel": st.column_config.NumberColumn("Nivel (1-9)", min_value=1, max_value=9, step=1),
            "evidencia": st.column_config.TextColumn("Evidencia / notas"),
        },
    )

    puntaje = trl.calcular_trl(df_resp)
    st.metric("TRL estimado", f"{puntaje:.1f}" if puntaje is not None else "-")

    col_guardar, col_ayuda = st.columns([1, 1])
    with col_guardar:
        if st.button("Guardar evaluacion"):
            if puntaje is None:
                st.error("Define niveles validos (1-9) en al menos una dimension antes de guardar.")
            else:
                try:
                    save_trl_result(project_id, df_resp, float(puntaje))
                    st.success("Evaluacion guardada correctamente.")
                except Exception as error:
                    st.error(f"Error al guardar: {error}")

    with col_ayuda:
        st.info(
            "El guardado crea un registro por dimension y asocia el TRL global a la misma fecha de evaluacion para el proyecto seleccionado."
        )
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown("### Evaluación IRL")
    st.caption(
        "Responde las preguntas de cada pestaña y acredita la evidencia para calcular automáticamente el nivel de madurez por dimensión."
    )
    _init_irl_state()
    tabs = st.tabs([dimension for dimension, _ in IRL_DIMENSIONS])
    for idx, (dimension, _) in enumerate(IRL_DIMENSIONS):
        with tabs[idx]:
            if dimension == "CRL":
                _render_crl_tab()
            else:
                _render_placeholder_tab(dimension)
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell section-shell--split'>", unsafe_allow_html=True)
    st.markdown("#### Radar IRL interactivo")
    radar_col_left, radar_col_right = st.columns([1.1, 1])
    with radar_col_left:
        st.caption("Los niveles mostrados se ajustan automáticamente según la evaluación registrada en las pestañas superiores.")
        _init_irl_state()
        radar_values = {}
        for dimension, _ in IRL_DIMENSIONS:
            valor = st.session_state["irl_scores"].get(dimension, 0)
            radar_values[dimension] = valor
        resumen_df = (
            pd.DataFrame(
                [
                    {"Dimensión": dimension, "Nivel": radar_values.get(dimension, 0)}
                    for dimension, _ in IRL_DIMENSIONS
                ]
            )
            .set_index("Dimensión")
        )
        st.dataframe(resumen_df, use_container_width=True)

    with radar_col_right:
        labels = list(radar_values.keys())
        values = list(radar_values.values())
        values_cycle = values + values[:1]
        theta = labels + labels[:1]
        radar_fig = go.Figure()
        radar_fig.add_trace(
            go.Scatterpolar(
                r=values_cycle,
                theta=theta,
                fill="toself",
                name="Perfil IRL",
                line_color="#3f8144",
                fillcolor="rgba(63, 129, 68, 0.25)",
            )
        )
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 9])),
            template="plotly_white",
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(radar_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.subheader("Historial del proyecto")

    historial = get_trl_history(project_id)
    if historial.empty:
        st.warning("Aun no existe historial TRL para este proyecto.")
    else:
        ultimo_registro = historial["fecha_eval"].iloc[0]
        st.caption(f"Ultima evaluacion registrada: {ultimo_registro}")
        st.dataframe(historial, use_container_width=True, hide_index=True)

        datos_ultimo = historial[historial["fecha_eval"] == ultimo_registro].copy()
        pivot = datos_ultimo.groupby("dimension", as_index=False)["nivel"].mean()
        dimensiones_ids = trl.ids_dimensiones()
        dimensiones_labels = trl.labels_dimensiones()

        pivot["orden"] = pivot["dimension"].apply(lambda dim: dimensiones_ids.index(dim) if dim in dimensiones_ids else 999)
        pivot = pivot.sort_values("orden")
        valores = []
        for dim_id in dimensiones_ids:
            registro = pivot.loc[pivot["dimension"] == dim_id, "nivel"]
            valores.append(float(registro.values[0]) if len(registro) > 0 and pd.notna(registro.values[0]) else np.nan)

        angles = np.linspace(0, 2 * np.pi, len(dimensiones_labels), endpoint=False).tolist()
        valores_ciclo = valores + valores[:1]
        angulos_ciclo = angles + angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(dimensiones_labels)
        ax.set_rlabel_position(0)
        ax.set_yticks([1, 3, 5, 7, 9])
        ax.set_ylim(0, 9)

        ax.plot(angulos_ciclo, valores_ciclo, linewidth=2, color="#3f8144")
        ax.fill(angulos_ciclo, valores_ciclo, alpha=0.25, color="#3f8144")

        st.pyplot(fig)

        st.download_button(
            "Descargar historial TRL (CSV)",
            data=historial.to_csv(index=False).encode("utf-8"),
            file_name=f"trl_historial_{seleccion}.csv",
            mime="text/csv",
        )
    st.markdown("</div>", unsafe_allow_html=True)
