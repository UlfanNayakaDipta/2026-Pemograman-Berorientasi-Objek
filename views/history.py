"""CoreDoc – History page (Streamlit)."""

import streamlit as st

from models.history_model import HistoryModel
from config import CONVERTED_DIR
from components.ui import section_header

st.set_page_config(page_title="CoreDoc | History", layout="wide")

history = HistoryModel()
records = history.get_all_records()

col_header, col_btn = st.columns([4, 1])
with col_header:
    section_header(
        "Activity History",
        "Track all your offline conversions and extractions here. Stored locally in SQLite.",
    )
with col_btn:
    if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
        history.clear_all()
        st.rerun()

if not records:
    st.info("No history records found. Try converting some files!")
    st.stop()

# Render as table rows
for r in records:
    cols = st.columns([1.5, 1, 1.5, 2])
    with cols[0]:
        st.caption(r["created_at"])

    with cols[1]:
        mod = r["module_name"]
        if mod == "Word to PDF":
            st.markdown('<span class="badge badge-cyan">Word to PDF</span>', unsafe_allow_html=True)
        elif mod == "PDF to Word":
            st.markdown('<span class="badge badge-emerald">PDF to Word</span>', unsafe_allow_html=True)
        elif mod == "Smart OCR":
            st.markdown('<span class="badge badge-purple">Smart OCR</span>', unsafe_allow_html=True)
        else:
            st.write(mod)

    with cols[2]:
        st.write(r["original_filename"])

    with cols[3]:
        data = r["result_data"]
        if data.startswith("["):  # JSON batch
            import json
            try:
                files = json.loads(data)
                with st.popover(f"📁 View {len(files)} Files", use_container_width=True):
                    for fname in files:
                        fp = CONVERTED_DIR / fname
                        if fp.exists():
                            with open(fp, "rb") as fh:
                                st.download_button(
                                    f"📄 {fname[:25]}..." if len(fname) > 25 else f"📄 {fname}",
                                    data=fh,
                                    file_name=fname,
                                    key=f"hist_{r['id']}_{fname}",
                                    use_container_width=True,
                                )
                        else:
                            st.caption(f"{fname[:25]}... (expired)")
            except Exception:
                st.caption("Invalid batch data")
        elif data.startswith("CoreDoc_"):
            fp = CONVERTED_DIR / data
            if fp.exists():
                with open(fp, "rb") as fh:
                    st.download_button(
                        "⬇️ Download File",
                        data=fh,
                        file_name=data,
                        key=f"hist_{r['id']}",
                        use_container_width=True,
                    )
            else:
                st.caption(f"{data[:25]}... (expired)")
        else:
            with st.popover("📝 View Extracted Text", use_container_width=True):
                st.text_area("OCR Result", value=data, height=250, label_visibility="collapsed", key=f"hist_txt_{r['id']}")

    st.divider()
