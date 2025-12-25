"""Protocol definition for OCR backends."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class OCRBackend(Protocol):
    """Protocol for OCR backend implementations.

    This protocol defines the interface that all OCR backends must implement.
    Uses structural subtyping (duck typing with type safety).
    """

    def perform_ocr(self, image_path: str) -> str:
        """Perform OCR on an image and return the extracted text.

        Args:
            image_path: Path to the image file to process.

        Returns:
            Recognized text from the image.
        """
        ...
