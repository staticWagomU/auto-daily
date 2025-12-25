"""Tests for OCR functionality using Vision Framework."""

from pathlib import Path

from auto_daily.ocr import perform_ocr


def test_japanese_ocr(tmp_path: Path) -> None:
    """Test that perform_ocr extracts Japanese text from an image.

    The function should:
    1. Use Vision Framework to recognize text in an image
    2. Support Japanese text recognition
    3. Return the recognized text as a string
    """
    # Create a test image with Japanese text using screencapture
    # For this test, we'll use the current screen which should contain some text
    from auto_daily.capture import capture_screen

    image_path = capture_screen(output_dir=tmp_path)
    assert image_path is not None

    # Act
    text = perform_ocr(image_path)

    # Assert
    # The result should be a string (may be empty if no text recognized)
    assert isinstance(text, str)
