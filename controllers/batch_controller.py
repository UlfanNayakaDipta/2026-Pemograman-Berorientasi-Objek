import io
import uuid
import zipfile
from pathlib import Path
from flask import Blueprint, send_file, abort

from config import CONVERTED_DIR

batch_bp = Blueprint("batch", __name__, url_prefix="/batch")

# Store batch ID to list of converted filenames
batch_store: dict[str, list[str]] = {}

def register_batch(filenames: list[str]) -> str:
    """Registers a list of filenames for ZIP download and returns a batch_id."""
    batch_id = uuid.uuid4().hex
    batch_store[batch_id] = filenames
    return batch_id

@batch_bp.route("/download-zip/<batch_id>", methods=["GET"])
def download_zip(batch_id: str):
    filenames = batch_store.get(batch_id)
    if not filenames:
        return abort(404, "Batch not found or expired.")
        
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
        download_name="CoreDoc_Batch_Results.zip"
    )
