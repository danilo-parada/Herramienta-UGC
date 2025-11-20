from __future__ import annotations

import streamlit as st


def render_irl_banner(
    title: str = "Medición del Nivel de Madurez de EBCTs",
    subtitle: str = (
        "Herramienta de autoevaluación que diagnostica el estado actual de una "
        "Empresa de Base Científico-Tecnológica en seis dimensiones clave: TRL, BRL, IPRL, TmRL, FRL y CRL."
    ),
    body: str = (
        "Basada en el modelo KTH Innovation Readiness Level™, esta evaluación orienta los próximos pasos hacia la "
        "consolidación e internacionalización de su EBCT. Para un diagnóstico dinámico y seguimiento continuo, visite "
        "www.calculadorarl.cl."
    ),
):
    """
    Renderiza un banner institucional reutilizable para la "Hoja de IRL".
    - Estilo coherente con Trayectoria EBCT (gradiente, tipografía moderna, micro-iconos/pictogramas)
    - Responsive (desktop y móvil)
    - Botón de acceso rápido a Calculadora RL
    """

    # CSS con nombres de clase con prefijo para evitar colisiones
    st.markdown(
        """
        <style>
        :root {
            --tray-irl-bg1: #0f3b4c; /* azul petróleo */
            --tray-irl-bg2: #1b5e20; /* verde institucional */
            --tray-irl-fg: #ffffff;
            --tray-irl-fg-subtle: rgba(255,255,255,0.85);
            --tray-irl-fg-muted: rgba(255,255,255,0.7);
            --tray-irl-accent: #9be7a6; /* verde suave para acentos */
            --tray-irl-shadow: rgba(0,0,0,0.15);
        }

        .tray-irl-banner {
            border-radius: 12px;
            background: linear-gradient(120deg, var(--tray-irl-bg1) 0%, var(--tray-irl-bg2) 100%);
            color: var(--tray-irl-fg);
            padding: 20px 24px;
            margin: 8px 0 18px 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 2px 10px var(--tray-irl-shadow);
        }
        .tray-irl-banner__inner {
            display: grid;
            grid-template-columns: 1fr; /* una sola columna para simplificar y mejorar responsive */
            gap: 18px;
            align-items: center;
        }
        .tray-irl-banner__title {
            margin: 0 0 4px 0;
            font-weight: 700;
            font-size: 1.25rem; /* ~20px */
            letter-spacing: 0.2px;
            color: #ffffff !important; /* forzar blanco */
            font-family: Inter, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
        }
        .tray-irl-banner__subtitle {
            margin: 0 0 8px 0;
            color: #ffffff !important; /* forzar blanco sobre fondo verde/azul */
            line-height: 1.35;
            font-size: 0.98rem;
            font-family: Inter, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
        }
        .tray-irl-banner__body {
            margin: 0 0 12px 0;
            color: #ffffff !important; /* forzar blanco sobre fondo verde/azul */
            line-height: 1.35;
            font-size: 0.9rem;
            font-family: Inter, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
        }
        .tray-irl-banner__icons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 6px;
        }
        .tray-irl-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.1);
            color: #ffffff !important; /* forzar blanco en chips */
            border: 1px solid rgba(255,255,255,0.18);
            font-size: 0.8rem;
            white-space: nowrap;
            font-family: Inter, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
        }
        .tray-irl-chip svg {
            width: 16px;
            height: 16px;
            display: block;
        }
        /* Se retiran estilos del botón CTA y columna derecha */

        .tray-irl-divider {
            position: absolute;
            left: 0; right: 0; bottom: 0;
            height: 4px;
            background: linear-gradient(90deg, rgba(255,255,255,0) 0%, var(--tray-irl-accent) 50%, rgba(255,255,255,0) 100%);
            opacity: 0.9;
        }

        @media (max-width: 900px) {
            .tray-irl-banner__inner { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Íconos minimalistas como pictogramas con iniciales en círculos
    # (alternativa robusta a icon fonts externas)
    def chip(label: str, title: str) -> str:
        initials = label
        svg = f'''
        <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="10" cy="10" r="9" fill="rgba(255,255,255,0.18)" stroke="rgba(255,255,255,0.35)" stroke-width="1.2" />
            <text x="10" y="12" text-anchor="middle" font-size="8" font-family="Inter, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif" fill="#ffffff">{initials}</text>
        </svg>
        '''
        return f'<span class="tray-irl-chip" title="{title}">{svg}<span>{title}</span></span>'

    chips_html = "".join(
        [
            chip("TRL", "Tecnología (TRL)"),
            chip("BRL", "Negocio (BRL)"),
            chip("IP", "Propiedad Intelectual (IPRL)"),
            chip("Tm", "Equipo (TmRL)"),
            chip("FRL", "Financiamiento (FRL)"),
            chip("CRL", "Cliente/Mercado (CRL)"),
        ]
    )

    html = f"""
    <div class=\"tray-irl-banner\">
        <div class=\"tray-irl-banner__inner\">
            <div>
                <h3 class=\"tray-irl-banner__title\">{title}</h3>
                <p class=\"tray-irl-banner__subtitle\">{subtitle}</p>
                <p class=\"tray-irl-banner__body\">{body}</p>
                <div class=\"tray-irl-banner__icons\">{chips_html}</div>
            </div>
        </div>
        <div class=\"tray-irl-divider\"></div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
