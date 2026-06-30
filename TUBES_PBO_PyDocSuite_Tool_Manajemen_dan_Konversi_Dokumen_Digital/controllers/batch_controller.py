import io
import json
import uuid
import zipfile
from pathlib import Path
from flask import Blueprint, send_file, abort

from config import CONVERTED_DIR

batch_bp = Blueprint("batch", __name__, url_prefix="/batch")

BATCH_STORE_DIR = CONVERTED_DIR / ".batch_meta"


def _batch_path(batch_id: str) -> Path:
    BATCH_STORE_DIR.mkdir(parents=True, exist_ok=True)
    return BATCH_STORE_DIR / f"{batch_id}.json"


def register_batch(filenames: list[str]) -> str:
    """Registers a list of filenames for ZIP download and returns a batch_id."""
    batch_id = uuid.uuid4().hex
    _batch_path(batch_id).write_text(json.dumps(filenames), encoding="utf-8")
    return batch_id


@batch_bp.route("/download-zip/<batch_id>", methods=["GET"])
def download_zip(batch_id: str):
    path = _batch_path(batch_id)
    if not path.exists():
        return abort(404, "Batch not found or expired.")

    filenames: list[str] = json.loads(path.read_text(encoding="utf-8"))

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in filenames:
            file_path = CONVERTED_DIR / filename
            if file_path.exists():
                zf.write(file_path, arcname=filename)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="CoreDoc_Batch_Results.zip",
    )
