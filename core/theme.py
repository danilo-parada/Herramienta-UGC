from __future__ import annotations

from pathlib import Path

import streamlit as st


def load_theme() -> None:
    """Inject the shared visual theme for the INFOR experience."""
    css_path = Path(__file__).resolve().parent.parent / "assets" / "theme.css"
    if not css_path.exists():
        return

    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
