
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path
from core import db, utils, trl
from core.db_trl import save_trl_result, get_trl_history

IRL_DIMENSIONS = [
    ("CRL", 6),
    ("BRL", 5),
    ("TRL", 4),
    ("IPRL", 5),
    ("TmRL", 6),
    ("FRL", 5),
]

st.title("Fase 1 - Evaluacion TRL")
st.caption("Radiografia del nivel de madurez tecnologica de cada proyecto a partir de seis dimensiones evaluables.")

fase0_page = next(Path("pages").glob("02_*_Fase_0_Portafolio.py"), None)
if fase0_page:
    st.markdown("<div style='padding:0.6rem 0;'>", unsafe_allow_html=True)
    if st.button('Volver a Fase 0', type='primary'):
        st.switch_page(str(fase0_page))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### Selecciona un proyecto del portafolio maestro")
df_port = utils.normalize_df(db.fetch_df())
if df_port.empty:
    st.warning("No hay proyectos en el portafolio. Registra iniciativas en Fase 0.")
    st.stop()


def fmt_opt(identificador: int) -> str:
    fila = df_port.loc[df_port["id_innovacion"] == identificador]
    if fila.empty:
        return str(identificador)
    return f"{identificador} - {fila['nombre_innovacion'].values[0]}"


ids = df_port["id_innovacion"].tolist()
seleccion = st.selectbox("Proyecto", ids, format_func=fmt_opt)

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
                save_trl_result(int(seleccion), df_resp, float(puntaje))
                st.success("Evaluacion guardada correctamente.")
            except Exception as error:
                st.error(f"Error al guardar: {error}")

with col_ayuda:
    st.info(
        "El guardado crea un registro por dimension y asocia el TRL global a la misma fecha de evaluacion para el proyecto seleccionado."
    )

st.divider()
st.subheader("Radar IRL interactivo")
radar_col_left, radar_col_right = st.columns([1.1, 1])
with radar_col_left:
    st.caption("Ajusta los niveles (0-9) para visualizar el perfil IRL estimado antes de registrar evidencias.")
    radar_values = {label: st.slider(label, 0, 9, default) for label, default in IRL_DIMENSIONS}

with radar_col_right:
    labels = list(radar_values.keys())
    values = list(radar_values.values())
    values_cycle = values + values[:1]
    theta = labels + labels[:1]
    radar_fig = go.Figure()
    radar_fig.add_trace(
        go.Scatterpolar(r=values_cycle, theta=theta, fill="toself", name="Perfil IRL", line_color="#1D4ED8")
    )
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 9])),
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(radar_fig, use_container_width=True)

st.divider()
st.subheader("Historial del proyecto")

historial = get_trl_history(int(seleccion))
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

    ax.plot(angulos_ciclo, valores_ciclo, linewidth=2, color="#3bacb6")
    ax.fill(angulos_ciclo, valores_ciclo, alpha=0.2, color="#3bacb6")

    st.pyplot(fig)

    st.download_button(
        "Descargar historial TRL (CSV)",
        data=historial.to_csv(index=False).encode("utf-8"),
        file_name=f"trl_historial_{seleccion}.csv",
        mime="text/csv",
    )
