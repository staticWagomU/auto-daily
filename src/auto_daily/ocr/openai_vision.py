"""OpenAI Vision OCR backend implementation."""

import base64

from openai import OpenAI

from auto_daily.config import get_ocr_model, get_openai_api_key


class OpenAIVisionOCR:
    """OCR backend using OpenAI's Vision API (GPT-4o).

    Implements the OCRBackend protocol for use with the OCR abstraction layer.
    Uses OpenAI's multimodal capabilities to extract text from images.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """Initialize the OpenAI Vision OCR client.

        Args:
            api_key: OpenAI API key.
                    Uses OPENAI_API_KEY env var if not specified.
            model: Model name to use (e.g., "gpt-4o-mini").
                  Uses OCR_MODEL env var or default if not specified.
        """
        self.api_key = api_key if api_key is not None else get_openai_api_key()
        self.model = model if model is not None else get_ocr_model()
        self.client = OpenAI(api_key=self.api_key)

    def perform_ocr(self, image_path: str) -> str:
        """Perform OCR on an image using OpenAI Vision API.

        Args:
            image_path: Path to the image file to process.

        Returns:
            Recognized text from the image.
        """
        # Read and encode the image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Determine the image type from extension
        image_path_lower = image_path.lower()
        if image_path_lower.endswith(".png"):
            media_type = "image/png"
        elif image_path_lower.endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        elif image_path_lower.endswith(".gif"):
            media_type = "image/gif"
        elif image_path_lower.endswith(".webp"):
            media_type = "image/webp"
        else:
            media_type = "image/png"  # Default to PNG

        # Call OpenAI Vision API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "この画像に含まれるすべてのテキストを抽出してください。テキストのみを出力し、説明は不要です。",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
        )

        content = response.choices[0].message.content
        return content if content is not None else ""
