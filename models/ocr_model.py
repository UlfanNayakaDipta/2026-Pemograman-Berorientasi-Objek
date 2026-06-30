from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import easyocr
from PIL import UnidentifiedImageError

class OcrError(RuntimeError):
    """Raised when OCR processing fails."""


@dataclass(frozen=True)
class OcrResult:
    extracted_text: str


class OcrEngine:
    """Extract text from images using EasyOCR."""

    allowed_extensions: Final[set[str]] = {".png", ".jpg", ".jpeg"}

    def __init__(self) -> None:
        # Initialize the reader only once. This will download the model to ~/.EasyOCR 
        # on the first run if it's not already there.
        # We specify English ('en') and Indonesian ('id').
        try:
            self.reader = easyocr.Reader(['en', 'id'], verbose=False)
        except Exception as exc:
            raise OcrError(f"Failed to initialize EasyOCR: {str(exc)}") from exc

    def extract_text(self, image_path: Path) -> OcrResult:
        self._validate_image_path(image_path)

        try:
            # EasyOCR can directly take a file path
            results = self.reader.readtext(str(image_path.absolute()), detail=0, paragraph=True)
            
            extracted_text = "\n\n".join(results)
                
            if not extracted_text or not extracted_text.strip():
                raise OcrError("No readable text could be extracted from the image.")
                
            return OcrResult(extracted_text=extracted_text.strip())
            
        except Exception as exc:
            # We catch generic exceptions because deep learning libraries can throw various errors
            raise OcrError(f"An unexpected error occurred during OCR: {str(exc)}") from exc

    def _validate_image_path(self, image_path: Path) -> None:
        if not image_path.exists():
            raise OcrError("The uploaded image was not found on disk.")
        if not image_path.is_file():
            raise OcrError("The uploaded image path is not a file.")
        if image_path.suffix.lower() not in self.allowed_extensions:
            raise OcrError("Only .png, .jpg, and .jpeg files are supported.")
