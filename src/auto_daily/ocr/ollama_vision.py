"""Ollama Vision OCR backend implementation."""

import base64

import httpx

from auto_daily.config import get_ocr_model, get_ollama_base_url


class OllamaVisionOCR:
    """OCR backend using Ollama's Vision models (llava, llama3.2-vision, etc.).

    Implements the OCRBackend protocol for use with the OCR abstraction layer.
    Uses Ollama's multimodal capabilities to extract text from images.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        """Initialize the Ollama Vision OCR client.

        Args:
            base_url: Ollama server URL.
                     Uses OLLAMA_BASE_URL env var or default if not specified.
            model: Vision model name to use (e.g., "llava").
                  Uses OCR_MODEL env var or "llava" if not specified.
        """
        self.base_url = base_url if base_url is not None else get_ollama_base_url()
        self.model = model if model is not None else get_ocr_model()

    def perform_ocr(self, image_path: str) -> str:
        """Perform OCR on an image using Ollama Vision API.

        Args:
            image_path: Path to the image file to process.

        Returns:
            Recognized text from the image.
        """
        # Read and encode the image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Call Ollama Vision API
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": "この画像に含まれるすべてのテキストを抽出してください。テキストのみを出力し、説明は不要です。",
                "images": [image_data],
                "stream": False,
            },
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["response"]
