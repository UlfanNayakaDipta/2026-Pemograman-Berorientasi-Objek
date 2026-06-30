from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import docx2pdf
import pythoncom

class ConversionError(RuntimeError):
    """Raised when Word to PDF conversion fails."""


@dataclass(frozen=True)
class ConversionResult:
    output_path: Path


class WordToPdfConverter:
    """Convert .doc and .docx files to PDF using docx2pdf and MS Word COM."""

    allowed_extensions: Final[set[str]] = {".doc", ".docx"}

    def convert(self, source_path: Path, output_dir: Path) -> ConversionResult:
        self._validate_source_path(source_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{source_path.stem}.pdf"
        
        # Initialize COM thread context for pythoncom (necessary when running within a Flask worker thread)
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass # Ignore if already initialized

        try:
            docx2pdf.convert(str(source_path.absolute()), str(output_path.absolute()))
        except Exception as exc:
            # Catching generic Exception because docx2pdf can throw various COM errors
            raise ConversionError(
                f"Conversion failed. Please ensure Microsoft Word is installed and working. Error: {str(exc)}"
            ) from exc
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

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
