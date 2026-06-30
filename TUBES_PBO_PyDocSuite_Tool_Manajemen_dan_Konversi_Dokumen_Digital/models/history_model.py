from __future__ import annotations

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from config import DB_PATH, CONVERTED_DIR


class HistoryModel:
    """
    Handles history tracking using an SQLite database.
    Because SQLite connections shouldn't be shared across threads blindly without care,
    we create short-lived connections for each operation.
    """
    
    # We use a lock to ensure table creation doesn't collide
    _init_lock = threading.Lock()
    _initialized = False

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        if HistoryModel._initialized:
            return
            
        with HistoryModel._init_lock:
            if HistoryModel._initialized:
                return
                
            # Create table if it doesn't exist
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_name TEXT NOT NULL,
                        original_filename TEXT NOT NULL,
                        result_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            HistoryModel._initialized = True

    def add_record(self, module_name: str, original_filename: str, result_data: str) -> None:
        """
        Add a new record to the history.
        result_data could be the converted filename or extracted text (for OCR).
        Automatically enforces a maximum of 20 records and deletes old converted files.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Insert new record
            cursor.execute("""
                INSERT INTO history_records (module_name, original_filename, result_data, created_at)
                VALUES (?, ?, ?, ?)
            """, (module_name, original_filename, result_data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 2. Enforce limit of 20
            cursor.execute("""
                SELECT id, result_data FROM history_records 
                ORDER BY created_at DESC, id DESC 
                LIMIT -1 OFFSET 20
            """)
            excess_records = cursor.fetchall()
            
            if excess_records:
                for row_id, r_data in excess_records:
                    # Clean up the physical file to save disk space
                    files_to_delete = []
                    if r_data.startswith("CoreDoc_"):
                        files_to_delete.append(r_data)
                    elif r_data.startswith("["):
                        import json
                        try:
                            files_to_delete.extend(json.loads(r_data))
                        except Exception:
                            pass
                            
                    for f_name in files_to_delete:
                        if isinstance(f_name, str) and f_name.startswith("CoreDoc_"):
                            file_path = CONVERTED_DIR / f_name
                            try:
                                if file_path.exists():
                                    file_path.unlink()
                            except OSError:
                                pass
                
                # Delete excess records from the database
                excess_ids = [row[0] for row in excess_records]
                placeholders = ",".join("?" for _ in excess_ids)
                cursor.execute(f"DELETE FROM history_records WHERE id IN ({placeholders})", excess_ids)

            conn.commit()

    def get_all_records(self) -> list[dict[str, Any]]:
        """
        Retrieve all history records, ordered by newest first.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, module_name, original_filename, result_data, created_at 
                FROM history_records 
                ORDER BY created_at DESC, id DESC
            """)
            rows = cursor.fetchall()
            
            # Convert to list of dicts for easier consumption in templates
            return [dict(row) for row in rows]

    def clear_all(self) -> None:
        """
        Deletes all history records from the database and removes all physical converted files.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Fetch all records to delete physical files
            cursor.execute("SELECT result_data FROM history_records")
            records = cursor.fetchall()
            
            for (r_data,) in records:
                files_to_delete = []
                if r_data.startswith("CoreDoc_"):
                    files_to_delete.append(r_data)
                elif r_data.startswith("["):
                    import json
                    try:
                        files_to_delete.extend(json.loads(r_data))
                    except Exception:
                        pass
                        
                for f_name in files_to_delete:
                    if isinstance(f_name, str) and f_name.startswith("CoreDoc_"):
                        file_path = CONVERTED_DIR / f_name
                        try:
                            if file_path.exists():
                                file_path.unlink()
                        except OSError:
                            pass
                            
            # 2. Clear database table
            cursor.execute("DELETE FROM history_records")
            conn.commit()
