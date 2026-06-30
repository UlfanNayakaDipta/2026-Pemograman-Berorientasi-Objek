from __future__ import annotations

import logging
from pathlib import Path
from dataclasses import dataclass

from pdf2docx import Converter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PdfToWordResult:
    output_path: Path


class PdfToWordConversionError(Exception):
    """Raised when PDF to Word conversion fails."""
    pass


class PdfToWordConverter:
    """
    Handles fully offline PDF to Word conversions using pdf2docx.
    """

    def convert(self, pdf_path: Path, output_dir: Path) -> PdfToWordResult:
        if not pdf_path.exists():
            raise PdfToWordConversionError(f"PDF file not found: {pdf_path.name}")
            
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{pdf_path.stem}.docx"
        cv = None

        try:
            # Initialize converter
            cv = Converter(str(pdf_path))
            
            # Perform conversion (all pages by default)
            cv.convert(str(output_path), start=0, end=None)
            
            if not output_path.exists():
                raise PdfToWordConversionError("Conversion completed but output file is missing.")
                
            return PdfToWordResult(output_path=output_path)
            
        except Exception as e:
            logger.exception("PDF to Word conversion failed.")
            raise PdfToWordConversionError(f"Failed to convert PDF: {str(e)}")
        finally:
            if cv:
                cv.close()
