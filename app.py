"""CoreDoc – Streamlit entrypoint with top navigation."""

import streamlit as st
from config import ensure_runtime_directories
from components.ui import apply_global_style, theme_toggle_widget

ensure_runtime_directories()

st.logo("logo.svg")

# ── Init theme state ──
if "cd_theme" not in st.session_state:
    from config import STORAGE_DIR
    theme_file = STORAGE_DIR / ".theme"
    theme = "light"
    if theme_file.exists():
        try:
            theme = theme_file.read_text().strip()
        except Exception:
            pass
    if theme not in ["light", "dark"]:
        theme = "light"
    st.session_state.cd_theme = theme

# ── Define pages for top navigation ──
word_pdf_page = st.Page("views/word_to_pdf.py", title="Word to PDF", default=True)
pdf_word_page = st.Page("views/pdf_to_word.py", title="PDF to Word")
ocr_page = st.Page("views/ocr.py", title="Smart OCR")
history_page = st.Page("views/history.py", title="History")

pg = st.navigation(
    [word_pdf_page, pdf_word_page, ocr_page, history_page],
    position="top",
)

apply_global_style(light=st.session_state.cd_theme == "light")
theme_toggle_widget()
pg.run()
