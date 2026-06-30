"""File upload / cleanup / ZIP helpers – ported from Flask controllers."""

import uuid
import io
import zipfile
from pathlib import Path

import streamlit as st

from config import UPLOAD_DIR, CONVERTED_DIR


def save_uploaded_file(uploaded_file, base_dir: Path = UPLOAD_DIR) -> Path:
    """Save a Streamlit UploadedFile to disk and return the path."""
    upload_id = uuid.uuid4().hex
    safe_name = f"{upload_id}_{uploaded_file.name}"
    dest = base_dir / safe_name
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dest


def cleanup_file(path: Path) -> None:
    """Remove a file quietly."""
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def create_batch_zip(filenames: list[str]) -> bytes:
    """Create an in-memory ZIP of multiple converted files."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in filenames:
            fp = CONVERTED_DIR / name
            if fp.exists():
                zf.write(fp, arcname=name)
    buf.seek(0)
    return buf.getvalue()
