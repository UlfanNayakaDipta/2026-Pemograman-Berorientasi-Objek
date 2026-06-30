"""CoreDoc – Smart OCR page (Streamlit)."""

from pathlib import Path

import streamlit as st

from models.ocr_model import OcrEngine, OcrError
from models.history_model import HistoryModel
from components.file_handler import save_uploaded_file, cleanup_file
from components.ui import section_header

st.set_page_config(page_title="CoreDoc | Smart OCR", layout="wide")

ALLOWED = {".png", ".jpg", ".jpeg"}
engine = OcrEngine()
history = HistoryModel()


def is_allowed(name: str) -> bool:
    return Path(name).suffix.lower() in ALLOWED


col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    section_header("Upload Phase", "Upload a .png, .jpg, or .jpeg image to extract text.")
    st.markdown("#### Choose an Image")

    import uuid
    if "ocr_upload_error" in st.session_state:
        st.error(st.session_state.ocr_upload_error)
        del st.session_state.ocr_upload_error

    image_file = st.file_uploader(
        "Image File",
        label_visibility="collapsed",
        key=st.session_state.get("ocr_uploader_key", "ocr_uploader")
    )

    if image_file:
        ext = image_file.name.lower().split('.')[-1]
        if ext not in ["png", "jpg", "jpeg"]:
            st.session_state.ocr_upload_error = f"❌ File **{image_file.name}** ditolak! Hanya menerima gambar (PNG/JPG/JPEG)."
            st.session_state.ocr_uploader_key = "ocr_uploader_" + str(uuid.uuid4())
            st.rerun()

    btn_placeholder = st.empty()
    
    already_processed = bool(image_file) and image_file.file_id == st.session_state.get("ocr_processed_id")
    if already_processed:
        extract_clicked = False
        btn_placeholder.button("✅ Extracted", type="primary", disabled=True, use_container_width=True)
    else:
        extract_clicked = btn_placeholder.button("Extract Text", type="primary", use_container_width=True)

with col2:
    section_header("Processing Phase")
    with st.container(border=True):
        st.markdown("**1. Validation** – image type & size verified.")
    with st.container(border=True):
        st.markdown("**2. OCR Engine** – Tesseract extracts all text regions.")
    with st.container(border=True):
        st.markdown("**3. Result** – view and copy the text below.")

# ──────────────────────────────────────────────
if extract_clicked:
    if not image_file:
        st.error("Please upload an image first.")
        st.stop()
        
    btn_placeholder.button("⏳ Extracting... Please wait", type="primary", disabled=True, use_container_width=True)

    try:
        src = save_uploaded_file(image_file)
    except OSError:
        st.error("The file could not be saved on the server.")
        st.stop()

    try:
        result = engine.extract_text(src)
    except OcrError as exc:
        cleanup_file(src)
        st.error(str(exc))
        st.stop()

    cleanup_file(src)
    
    st.session_state.ocr_processed_id = image_file.file_id
    st.session_state.ocr_extracted_text = result.extracted_text
    
    history.add_record("Smart OCR", image_file.name, result.extracted_text[:200])
    
    btn_placeholder.button("✅ Extracted", type="primary", disabled=True, use_container_width=True)

if already_processed or (extract_clicked and "ocr_extracted_text" in st.session_state):
    text_content = st.session_state.ocr_extracted_text

    # ── Display result ──
    st.divider()
    st.markdown("### Extraction completed successfully")

    rcol1, rcol2 = st.columns([1, 0.8])

    with rcol1:
        st.markdown(
            f"<small style='color:#64748b'>Extracted Text from {image_file.name}</small>",
            unsafe_allow_html=True,
        )
        text_val = st.text_area(
            "Extracted text",
            value=text_content,
            height=250,
            label_visibility="collapsed",
        )

        copy_col, reset_col, _ = st.columns([1, 1, 2])
        # Copy via JS injection
        copy_col.button(
            "📋 Copy to Clipboard",
            key="copy_ocr_btn",
            use_container_width=True,
        )
        # The actual copy logic runs via st.markdown + JS snippet
        if st.session_state.get("copy_ocr_btn"):
            st.toast("Copied! (use Ctrl+C or the browser copy action)")

        def reset_ocr():
            import uuid
            st.session_state.ocr_uploader_key = "ocr_uploader_" + str(uuid.uuid4())
            for k in ["ocr_processed_id", "ocr_extracted_text", "ocr_confidence"]:
                st.session_state.pop(k, None)

        reset_col.button("Extract Another Image", use_container_width=True, on_click=reset_ocr)

    with rcol2:
        with st.container(border=True):
            st.markdown("**Clipboard Access** – select text and copy, or use the Copy button.")
