from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
CONVERTED_DIR = STORAGE_DIR / "converted"
DB_PATH = STORAGE_DIR / "history.db"
MAX_CONTENT_LENGTH_BYTES = 25 * 1024 * 1024
SECRET_KEY = os.environ.get("PYDOCSUITE_SECRET_KEY", "pydocsuite-dev-secret-key")


def ensure_runtime_directories() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    CONVERTED_DIR.mkdir(parents=True, exist_ok=True)
