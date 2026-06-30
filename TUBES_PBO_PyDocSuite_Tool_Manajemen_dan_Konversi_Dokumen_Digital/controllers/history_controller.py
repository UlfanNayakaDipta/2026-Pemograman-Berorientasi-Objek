from pathlib import Path
from flask import Blueprint, render_template, send_file, abort

from models.history_model import HistoryModel
from config import CONVERTED_DIR

history_bp = Blueprint("history", __name__, url_prefix="/history")
history_model = HistoryModel()


@history_bp.route("/", methods=["GET"])
def index():
    records = history_model.get_all_records()
    return render_template("history.html", title="CoreDoc | History", records=records)

@history_bp.route("/download/<path:filename>", methods=["GET"])
def download_history_file(filename: str):
    if not filename.startswith("CoreDoc_"):
        abort(404)
        
    file_path = CONVERTED_DIR / filename
    if not file_path.exists():
        abort(404)
        
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )
