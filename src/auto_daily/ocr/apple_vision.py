"""Apple Vision Framework OCR implementation."""

import Vision  # type: ignore[import-untyped]
from Foundation import NSURL  # type: ignore[import-untyped]


class AppleVisionOCR:
    """OCR backend using macOS Vision Framework.

    Implements the OCRBackend protocol for use with the OCR abstraction layer.
    """

    def perform_ocr(self, image_path: str) -> str:
        """Perform OCR on an image using Vision Framework.

        Args:
            image_path: Path to the image file to process.

        Returns:
            Recognized text from the image.
        """
        image_url = NSURL.fileURLWithPath_(image_path)
        handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(  # type: ignore[attr-defined]
            image_url, None
        )

        request = Vision.VNRecognizeTextRequest.alloc().init()  # type: ignore[attr-defined]
        request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)  # type: ignore[attr-defined]
        request.setRecognitionLanguages_(["ja-JP", "en-US"])

        success, error = handler.performRequests_error_([request], None)

        if not success or error:
            return ""

        results = request.results()
        if not results:
            return ""

        text_lines = []
        for observation in results:
            top_candidate = observation.topCandidates_(1)
            if top_candidate:
                text_lines.append(top_candidate[0].string())

        return "\n".join(text_lines)


def validate_ocr_result(text: str) -> tuple[bool, str]:
    """Validate and clean OCR result text.

    Args:
        text: Raw OCR result text.

    Returns:
        A tuple of (is_valid, cleaned_text) where:
        - is_valid: True if the text is non-empty after cleaning
        - cleaned_text: The text with leading/trailing whitespace removed
    """
    cleaned = text.strip()
    return (len(cleaned) > 0, cleaned)
