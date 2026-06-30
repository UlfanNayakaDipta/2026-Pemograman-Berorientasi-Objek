from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from flask import Blueprint, flash, render_template, request, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import UPLOAD_DIR
from models.ocr_model import OcrEngine, OcrError
from models.history_model import HistoryModel

ocr_bp = Blueprint("ocr", __name__, url_prefix="/ocr")
ocr_engine = OcrEngine()
history_model = HistoryModel()
ALLOWED_EXTENSIONS: Final[set[str]] = {".png", ".jpg", ".jpeg"}


@dataclass(frozen=True)
class OcrRecord:
    source_path: Path
    original_filename: str
    extracted_text: str
    created_at: datetime


ocr_store: dict[str, OcrRecord] = {}


def is_allowed_image_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(uploaded_file: FileStorage) -> tuple[str, Path]:
    if not isinstance(uploaded_file.filename, str) or not uploaded_file.filename.strip():
        raise ValueError("A valid file name is required.")

    safe_name = secure_filename(uploaded_file.filename)
    if not safe_name:
        raise ValueError("The uploaded file name is invalid.")

    upload_id = uuid.uuid4().hex
    saved_path = UPLOAD_DIR / f"ocr_{upload_id}_{safe_name}"
    uploaded_file.save(saved_path)
    return safe_name, saved_path


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


@ocr_bp.route("/", methods=["GET"])
def index():
    return render_template("ocr/index.html", title="CoreDoc | Smart OCR")


@ocr_bp.route("/extract", methods=["POST"])
def extract_text():
    uploaded_file = request.files.get("image")
    if uploaded_file is None:
        flash("Please choose an image before extracting.", "error")
        return render_template("ocr/index.html", title="CoreDoc | Smart OCR"), 400

    if not isinstance(uploaded_file.filename, str) or not uploaded_file.filename.strip():
        flash("Please choose an image before extracting.", "error")
        return render_template("ocr/index.html", title="CoreDoc | Smart OCR"), 400

    if not is_allowed_image_file(uploaded_file.filename):
        flash("Only .png, .jpg, and .jpeg files are supported.", "error")
        return render_template("ocr/index.html", title="CoreDoc | Smart OCR"), 400

    try:
        original_filename, source_path = save_uploaded_file(uploaded_file)
    except OSError:
        return (
            render_template(
                "error.html",
                title="Upload Failed",
                message="The file could not be saved on the server.",
                back_url=url_for("ocr.index"),
            ),
            500,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("ocr/index.html", title="CoreDoc | Smart OCR"), 400

    try:
        ocr_result = ocr_engine.extract_text(source_path)
    except OcrError as exc:
        cleanup_file(source_path)
        return (
            render_template(
                "error.html",
                title="Extraction Failed",
                message=str(exc),
                back_url=url_for("ocr.index"),
            ),
            500,
        )

    # We can clean up the file immediately since we already have the text in memory.
    # If we wanted to show the image on the result page, we'd keep it or serve it.
    cleanup_file(source_path)

    extraction_id = uuid.uuid4().hex
    ocr_store[extraction_id] = OcrRecord(
        source_path=source_path,
        original_filename=original_filename,
        extracted_text=ocr_result.extracted_text,
        created_at=datetime.now(timezone.utc),
    )
    
    try:
        history_model.add_record("Smart OCR", original_filename, ocr_result.extracted_text)
    except Exception:
        pass # Ignore history save failure

    return render_template(
        "ocr/result.html",
        title="CoreDoc | OCR Result",
        extraction_id=extraction_id,
        original_filename=original_filename,
        extracted_text=ocr_result.extracted_text,
        reset_url=url_for("ocr.index"),
    )
