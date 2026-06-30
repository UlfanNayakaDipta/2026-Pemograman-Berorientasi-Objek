from __future__ import annotations

import subprocess
import concurrent.futures
import logging
import tempfile
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import docx2pdf
import pythoncom

logger = logging.getLogger(__name__)

CONVERSION_TIMEOUT: Final[int] = 60  # seconds


class ConversionError(RuntimeError):
    """Raised when Word to PDF conversion fails."""


@dataclass(frozen=True)
class ConversionResult:
    output_path: Path


def _kill_winword() -> None:
    """Force-kill any lingering WINWORD.EXE processes."""
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "WINWORD.EXE"],
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass


def _do_convert(source_path: Path, output_path: Path) -> None:
    """Run docx2pdf conversion (must be in a thread with COM init)."""
    pythoncom.CoInitialize()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_input = temp_dir_path / ("input" + source_path.suffix)
            temp_output = temp_dir_path / "output.pdf"
            
            shutil.copy2(source_path, temp_input)
            docx2pdf.convert(str(temp_input.absolute()), str(temp_output.absolute()))
            
            if temp_output.exists():
                shutil.copy2(temp_output, output_path)
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


class WordToPdfConverter:
    """Convert .doc and .docx files to PDF using docx2pdf and MS Word COM."""

    allowed_extensions: Final[set[str]] = {".doc", ".docx"}

    def _is_temp_file(self, path: Path) -> bool:
        return path.name.startswith("~$")

    def convert(self, source_path: Path, output_dir: Path) -> ConversionResult:
        self._validate_source_path(source_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{source_path.stem}.pdf"

        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = pool.submit(_do_convert, source_path, output_path)
            try:
                future.result(timeout=CONVERSION_TIMEOUT)
            except concurrent.futures.TimeoutError:
                _kill_winword()
                raise ConversionError(
                    f"Conversion timed out after {CONVERSION_TIMEOUT}s. "
                    "The file may be corrupted or currently open in Microsoft Word."
                )
            except Exception as exc:
                _kill_winword()
                raise ConversionError(
                    f"Conversion failed. Please ensure Microsoft Word is installed "
                    f"and the file is not corrupted. Error: {exc}"
                ) from exc
        finally:
            pool.shutdown(wait=False)

        if not output_path.exists():
            raise ConversionError("docx2pdf reported success, but no PDF file was created.")

        return ConversionResult(output_path=output_path)

    def _validate_source_path(self, source_path: Path) -> None:
        if not source_path.exists():
            raise ConversionError("The uploaded document was not found on disk.")
        if not source_path.is_file():
            raise ConversionError("The uploaded document path is not a file.")
        if source_path.suffix.lower() not in self.allowed_extensions:
            raise ConversionError("Only .doc and .docx files can be converted.")
        if self._is_temp_file(source_path):
            raise ConversionError("Temporary Word files (~$) cannot be converted.")
