"""CoreDoc – Word to PDF page (Streamlit)."""

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from config import CONVERTED_DIR
from models.word_to_pdf import WordToPdfConverter, ConversionError
from models.history_model import HistoryModel
from components.file_handler import save_uploaded_file, cleanup_file, create_batch_zip
from components.ui import section_header


def _safe_stem(name: str) -> str:
    """Minimal secure_filename – keeps alnum, dashes, dots."""
    import re
    stem = Path(name).stem
    stem = re.sub(r"[^\w\-. ]", "", stem).strip()
    return stem if stem else "document"

# ── Page config must be first Streamlit call ──
st.set_page_config(page_title="CoreDoc | Word to PDF", layout="wide")

ALLOWED = {".doc", ".docx"}
converter = WordToPdfConverter()
history = HistoryModel()


def is_allowed(name: str) -> bool:
    return Path(name).suffix.lower() in ALLOWED


def build_dl_name(original: str) -> str:
    import time
    stem = _safe_stem(original)
    return f"CoreDoc_{int(time.time())}_{stem}.pdf"


# ──────────────────────────────────────────────
# Layout: two columns (same ratio as Flask version)
# ──────────────────────────────────────────────
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    section_header("Upload Phase", "Upload a .doc or .docx file and convert it locally.")
    st.markdown("#### Choose a Word document")

    import uuid
    if "w2p_upload_error" in st.session_state:
        st.error(st.session_state.w2p_upload_error)
        del st.session_state.w2p_upload_error

    uploaded_files = st.file_uploader(
        "Word File",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=st.session_state.get("w2p_uploader_key", "w2p_uploader")
    )

    if uploaded_files:
        invalid = [f for f in uploaded_files if not (f.name.lower().endswith(".doc") or f.name.lower().endswith(".docx"))]
        if invalid:
            st.session_state.w2p_upload_error = f"❌ File **{invalid[0].name}** ditolak! Hanya menerima file Word (.doc / .docx)."
            st.session_state.w2p_uploader_key = "w2p_uploader_" + str(uuid.uuid4())
            st.rerun()
            
    btn_placeholder = st.empty()
    
    current_file_ids = [f.file_id for f in uploaded_files] if uploaded_files else []
    already_processed = bool(uploaded_files) and current_file_ids == st.session_state.get("w2p_processed_ids", [])
    
    if already_processed:
        convert_clicked = False
        btn_placeholder.button("✅ Converted", type="primary", disabled=True, use_container_width=True)
    else:
        convert_clicked = btn_placeholder.button("Convert to PDF", type="primary", use_container_width=True)

with col2:
    section_header("Processing Phase")
    with st.container(border=True):
        st.markdown("**1. Validation** – file type, name & size verified.")
    with st.container(border=True):
        st.markdown("**2. Conversion** – MS Word COM via docx2pdf.")
    with st.container(border=True):
        st.markdown("**3. Result** – download your PDF below.")

# ──────────────────────────────────────────────
# Conversion logic
# ──────────────────────────────────────────────
if convert_clicked:
    if not uploaded_files:
        st.error("Please choose Word documents before converting.")
        st.stop()

    btn_placeholder.button("⏳ Converting... Please wait", type="primary", disabled=True, use_container_width=True)

    conversions = []
    failed = []
    dl_filenames = []

    for f in uploaded_files:
        try:
            src = save_uploaded_file(f)
        except OSError:
            failed.append((f.name, "Upload Failed on Server"))
            continue

        try:
            result = converter.convert(src, CONVERTED_DIR)
        except ConversionError as exc:
            cleanup_file(src)
            failed.append((f.name, str(exc)))
            continue

        cleanup_file(src)

        dl_name = build_dl_name(f.name)
        final_path = CONVERTED_DIR / dl_name
        try:
            result.output_path.rename(final_path)
        except Exception:
            import shutil
            shutil.move(str(result.output_path), str(final_path))
            
        dl_filenames.append(dl_name)
        conversions.append(
            {"original": f.name, "result": dl_name, "path": final_path}
        )

    # Save to history
    if conversions:
        if len(conversions) == 1:
            history.add_record("Word to PDF", conversions[0]["original"], conversions[0]["result"])
        else:
            import json
            data = json.dumps([c["result"] for c in conversions])
            history.add_record("Word to PDF", f"Batch ({len(conversions)} files)", data)
            
    st.session_state.w2p_processed_ids = current_file_ids
    st.session_state.w2p_conversions = conversions
    st.session_state.w2p_failed = failed
    st.session_state.w2p_dl_filenames = dl_filenames
    
    btn_placeholder.button("✅ Converted", type="primary", disabled=True, use_container_width=True)

# Always try to render results if they exist for current files
if already_processed or (convert_clicked and (st.session_state.get("w2p_conversions") or st.session_state.get("w2p_failed"))):
    conversions = st.session_state.w2p_conversions
    failed = st.session_state.w2p_failed
    dl_filenames = st.session_state.w2p_dl_filenames

    if not conversions and not failed:
        st.error("No valid files to process.")
        st.stop()

    # ── Display results ──
    st.divider()
    st.markdown("### Conversion completed successfully")

    rcol1, rcol2 = st.columns([1, 0.8])

    with rcol1:
        for conv in conversions:
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.markdown(
                    f"<small style='color:#64748b'>Source: {conv['original']}</small>  "
                    f"**{conv['result']}**",
                    unsafe_allow_html=True,
                )
                with open(conv["path"], "rb") as pf:
                    cc2.download_button(
                        "Download",
                        data=pf,
                        file_name=conv["result"],
                        mime="application/pdf",
                        key=f"dl_{conv['result']}",
                        use_container_width=True,
                    )

        for name, reason in failed:
            st.error(f"**{name}**: {reason}")

        def reset_w2p():
            import uuid
            st.session_state.w2p_uploader_key = "w2p_uploader_" + str(uuid.uuid4())
            for k in ["w2p_processed_ids", "w2p_conversions", "w2p_failed", "w2p_dl_filenames"]:
                st.session_state.pop(k, None)

        if len(dl_filenames) > 1:
            col_a, col_b, _ = st.columns([1, 1, 2])
            zip_bytes = create_batch_zip(dl_filenames)
            col_a.download_button(
                "Download All (ZIP)",
                data=zip_bytes,
                file_name="CoreDoc_Batch_Results.zip",
                mime="application/zip",
                use_container_width=True,
            )
            col_b.button(
                "Convert More",
                on_click=reset_w2p,
                use_container_width=True,
            )
        else:
            st.button(
                "Convert More",
                on_click=reset_w2p,
                use_container_width=True,
            )

    with rcol2:
        with st.container(border=True):
            st.markdown("**Ready to download** – PDFs are ready until you leave.")
        with st.container(border=True):
            st.markdown("**Reset** – click Convert More to start over.")
