from __future__ import annotations

import uuid
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from flask import Blueprint, flash, render_template, request, send_file, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import CONVERTED_DIR, UPLOAD_DIR
from models.word_to_pdf import ConversionError, WordToPdfConverter
from models.history_model import HistoryModel
from controllers.batch_controller import register_batch

word_pdf_bp = Blueprint("word_pdf", __name__)
converter = WordToPdfConverter()
history_model = HistoryModel()
ALLOWED_EXTENSIONS: Final[set[str]] = {".doc", ".docx"}


@dataclass(frozen=True)
class ConversionRecord:
    source_path: Path
    pdf_path: Path
    original_filename: str
    download_filename: str
    created_at: datetime


conversion_store: dict[str, ConversionRecord] = {}


def is_allowed_word_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def build_download_filename(original_filename: str) -> str:
    base_name = secure_filename(Path(original_filename).stem) or "document"
    return f"CoreDoc_{base_name}.pdf"


def save_uploaded_file(uploaded_file: FileStorage) -> tuple[str, Path]:
    if not isinstance(uploaded_file.filename, str) or not uploaded_file.filename.strip():
        raise ValueError("A valid file name is required.")

    safe_name = secure_filename(uploaded_file.filename)
    if not safe_name:
        raise ValueError("The uploaded file name is invalid.")

    upload_id = uuid.uuid4().hex
    saved_path = UPLOAD_DIR / f"{upload_id}_{safe_name}"
    uploaded_file.save(saved_path)
    return safe_name, saved_path


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


@word_pdf_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="PyDocSuite | Word to PDF Converter")


@word_pdf_bp.route("/convert", methods=["POST"])
def convert_word_to_pdf():
    uploaded_files = request.files.getlist("document")
    if not uploaded_files or not uploaded_files[0].filename:
        flash("Please choose Word documents before converting.", "error")
        return render_template("index.html", title="PyDocSuite | Word to PDF Converter"), 400

    for f in uploaded_files:
        if not isinstance(f.filename, str) or not f.filename.strip():
            continue
        if not is_allowed_word_file(f.filename):
            flash(f"Only .doc and .docx files are supported. File '{f.filename}' is invalid.", "error")
            return render_template("index.html", title="PyDocSuite | Word to PDF Converter"), 400

    conversions = []
    failed_files = []
    downloadable_filenames = []

    for uploaded_file in uploaded_files:
        if not isinstance(uploaded_file.filename, str) or not uploaded_file.filename.strip():
            continue
            
        try:
            original_filename, source_path = save_uploaded_file(uploaded_file)
        except OSError:
            failed_files.append((uploaded_file.filename, "Upload Failed on Server"))
            continue
        except ValueError as exc:
            failed_files.append((uploaded_file.filename, str(exc)))
            continue

        try:
            conversion_result = converter.convert(source_path, CONVERTED_DIR)
        except ConversionError as exc:
            cleanup_file(source_path)
            failed_files.append((original_filename, str(exc)))
            continue

        cleanup_file(source_path)

        conversion_id = uuid.uuid4().hex
        download_filename = build_download_filename(original_filename)
        conversion_store[conversion_id] = ConversionRecord(
            source_path=source_path,
            pdf_path=conversion_result.output_path,
            original_filename=original_filename,
            download_filename=download_filename,
            created_at=datetime.now(timezone.utc),
        )
        downloadable_filenames.append(download_filename)
        conversions.append({
            "id": conversion_id,
            "original": original_filename,
            "result": download_filename,
            "download_url": url_for("word_pdf.download_converted_pdf", conversion_id=conversion_id)
        })

    if conversions:
        if len(conversions) == 1:
            try:
                history_model.add_record("Word to PDF", conversions[0]["original"], conversions[0]["result"])
            except Exception:
                pass
        else:
            try:
                result_data = json.dumps([c["result"] for c in conversions])
                history_model.add_record("Word to PDF", f"Batch ({len(conversions)} files)", result_data)
            except Exception:
                pass

    if not conversions and not failed_files:
        flash("No valid files to process.", "error")
        return render_template("index.html", title="PyDocSuite | Word to PDF Converter"), 400

    batch_id = register_batch(downloadable_filenames) if downloadable_filenames else None

    return render_template(
        "result.html",
        title="PyDocSuite | Conversion Ready",
        conversions=conversions,
        failed_files=failed_files,
        batch_id=batch_id,
        reset_url=url_for("word_pdf.index"),
    )


@word_pdf_bp.route("/download/<conversion_id>", methods=["GET"])
def download_converted_pdf(conversion_id: str):
    record = conversion_store.get(conversion_id)
    if record is None or not record.pdf_path.exists():
        return (
            render_template(
                "error.html",
                title="File Missing",
                message="The converted PDF is no longer available. Please convert the file again.",
                back_url=url_for("word_pdf.index"),
            ),
            404,
        )

    return send_file(
        record.pdf_path,
        as_attachment=True,
        download_name=record.download_filename,
        mimetype="application/pdf",
    )
