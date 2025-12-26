"""OCR backend abstraction layer.

This module provides a unified interface for interacting with different OCR backends.
"""

from auto_daily.config import get_ocr_backend_name, get_ocr_filter_noise
from auto_daily.ocr.apple_vision import AppleVisionOCR, validate_ocr_result
from auto_daily.ocr.filters import OCRFilter
from auto_daily.ocr.protocol import OCRBackend

__all__ = [
    "AppleVisionOCR",
    "OCRBackend",
    "OCRFilter",
    "get_ocr_backend",
    "perform_ocr",
    "validate_ocr_result",
]


def get_ocr_backend() -> OCRBackend:
    """Get the OCR backend based on the OCR_BACKEND environment variable.

    Returns an instance of the appropriate OCR backend based on the configured value.

    Returns:
        An OCR backend instance implementing the OCRBackend protocol.

    Raises:
        ValueError: If the configured backend is not supported.
    """
    backend_name = get_ocr_backend_name()

    if backend_name == "apple":
        return AppleVisionOCR()

    if backend_name == "openai":
        from auto_daily.ocr.openai_vision import OpenAIVisionOCR

        return OpenAIVisionOCR()

    if backend_name == "ollama":
        from auto_daily.ocr.ollama_vision import OllamaVisionOCR

        return OllamaVisionOCR()

    raise ValueError(f"Unknown OCR backend: {backend_name}")


def perform_ocr(image_path: str) -> str:
    """Perform OCR on an image using the configured backend.

    This is a backward-compatible function that uses the configured backend.
    By default, noise filtering is applied to clean up the OCR output.
    Set OCR_FILTER_NOISE=false to disable filtering.

    Args:
        image_path: Path to the image file to process.

    Returns:
        Recognized text from the image, optionally filtered.
    """
    backend = get_ocr_backend()
    text = backend.perform_ocr(image_path)

    # Apply noise filtering if enabled
    if get_ocr_filter_noise():
        ocr_filter = OCRFilter()
        text = ocr_filter.filter(text)

    return text
