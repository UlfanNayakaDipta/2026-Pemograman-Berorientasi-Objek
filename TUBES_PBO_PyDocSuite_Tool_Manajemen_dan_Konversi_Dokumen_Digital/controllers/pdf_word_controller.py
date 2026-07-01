from __future__ import annotations

import uuid
import json
from pathlib import Path
from typing import Final

from flask import Blueprint, flash, render_template, request, send_file, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import CONVERTED_DIR, UPLOAD_DIR
from models.pdf_word_model import PdfToWordConversionError, PdfToWordConverter
from models.history_model import HistoryModel
from controllers.batch_controller import register_batch

pdf_word_bp = Blueprint("pdf_word", __name__, url_prefix="/pdf-to-word")
converter = PdfToWordConverter()
history_model = HistoryModel()
ALLOWED_EXTENSIONS: Final[set[str]] = {".pdf"}





def is_allowed_pdf_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def build_download_filename(original_filename: str) -> str:
    base_name = secure_filename(Path(original_filename).stem) or "document"
    return f"CoreDoc_{base_name}.docx"


def save_uploaded_file(uploaded_file: FileStorage) -> tuple[str, Path]:
    if not isinstance(uploaded_file.filename, str) or not uploaded_file.filename.strip():
        raise ValueError("A valid file name is required.")

    safe_name = secure_filename(uploaded_file.filename)
    if not safe_name:
        raise ValueError("The uploaded file name is invalid.")

    upload_id = uuid.uuid4().hex
    saved_path = UPLOAD_DIR / f"{upload_id}{Path(safe_name).suffix}"
    uploaded_file.save(saved_path)
    return safe_name, saved_path


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


@pdf_word_bp.route("/", methods=["GET"])
def index():
    return render_template("pdf_word.html", title="PyDocSuite | PDF to Word Converter")


@pdf_word_bp.route("/convert", methods=["POST"])
def convert_pdf_to_word():
    uploaded_files = request.files.getlist("document")
    if not uploaded_files or not uploaded_files[0].filename:
        flash("Please choose PDF documents before converting.", "error")
        return render_template("pdf_word.html", title="PyDocSuite | PDF to Word Converter"), 400

    for f in uploaded_files:
        if not isinstance(f.filename, str) or not f.filename.strip():
            continue
        if not is_allowed_pdf_file(f.filename):
            flash(f"Only .pdf files are supported. File '{f.filename}' is invalid.", "error")
            return render_template("pdf_word.html", title="PyDocSuite | PDF to Word Converter"), 400

    from concurrent.futures import ThreadPoolExecutor, as_completed

    conversions = []
    failed_files = []
    downloadable_filenames = []

    tasks = []
    for uploaded_file in uploaded_files:
        if not isinstance(uploaded_file.filename, str) or not uploaded_file.filename.strip():
            continue
            
        try:
            original_filename, source_path = save_uploaded_file(uploaded_file)
            tasks.append((original_filename, source_path))
        except OSError:
            failed_files.append((uploaded_file.filename, "Upload Failed on Server"))
        except ValueError as exc:
            failed_files.append((uploaded_file.filename, str(exc)))

    def _convert_task(orig_name, src_path):
        try:
            conversion_result = converter.convert(src_path, CONVERTED_DIR)
            return True, orig_name, src_path, conversion_result, None
        except Exception as e:
            return False, orig_name, src_path, None, str(e)

    if tasks:
        # Gunakan maksimal 4 worker agar tidak membuat CPU kepanasan atau lag
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(_convert_task, t[0], t[1]) for t in tasks]
            for future in as_completed(futures):
                success, orig_name, src_path, conv_result, err_msg = future.result()
                cleanup_file(src_path)

                if success:
                    download_filename = build_download_filename(orig_name)
                    # Rename output to match download name so history/batch finds it
                    real_path = conv_result.output_path
                    desired_path = real_path.with_name(download_filename)
                    if real_path != desired_path:
                        if desired_path.exists():
                            desired_path.unlink()
                        real_path.rename(desired_path)
                    
                    downloadable_filenames.append(download_filename)
                    conversions.append({
                        "id": download_filename,
                        "original": orig_name,
                        "result": download_filename,
                        "download_url": url_for("pdf_word.download_converted_docx", filename=download_filename)
                    })
                else:
                    failed_files.append((orig_name, err_msg))

    if conversions:
        if len(conversions) == 1:
            try:
                history_model.add_record("PDF to Word", conversions[0]["original"], conversions[0]["result"])
            except Exception:
                pass
        else:
            try:
                result_data = json.dumps([c["result"] for c in conversions])
                history_model.add_record("PDF to Word", f"Batch ({len(conversions)} files)", result_data)
            except Exception:
                pass

    if not conversions and not failed_files:
        flash("No valid files to process.", "error")
        return render_template("pdf_word.html", title="PyDocSuite | PDF to Word Converter"), 400

    batch_id = register_batch(downloadable_filenames) if downloadable_filenames else None

    return render_template(
        "pdf_word_result.html",
        title="PyDocSuite | Conversion Ready",
        conversions=conversions,
        failed_files=failed_files,
        batch_id=batch_id,
        reset_url=url_for("pdf_word.index"),
    )


@pdf_word_bp.route("/download/<filename>", methods=["GET"])
def download_converted_docx(filename: str):
    safe_name = secure_filename(filename)
    if not safe_name.startswith("CoreDoc_"):
        return render_template("error.html", title="Invalid File", message="Invalid filename.", back_url=url_for("pdf_word.index")), 404

    file_path = CONVERTED_DIR / safe_name
    if not file_path.exists():
        return render_template("error.html", title="File Missing", message="The converted document is no longer available. Please convert the file again.", back_url=url_for("pdf_word.index")), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=safe_name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
