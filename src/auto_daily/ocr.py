"""OCR module using macOS Vision Framework."""

import Vision  # type: ignore[import-untyped]
from Foundation import NSURL  # type: ignore[import-untyped]


def perform_ocr(image_path: str) -> str:
    """Perform OCR on an image using Vision Framework.

    Args:
        image_path: Path to the image file to process.

    Returns:
        Recognized text from the image.
    """
    image_url = NSURL.fileURLWithPath_(image_path)
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(image_url, None)

    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
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
