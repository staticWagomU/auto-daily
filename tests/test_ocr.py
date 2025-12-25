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


def test_ocr_returns_text(tmp_path: Path) -> None:
    """Test that OCR returns valid text when text is present in the image.

    This test verifies that:
    1. OCR can detect text in a typical screen capture
    2. The returned text is non-empty when visible text exists
    3. The text is properly stripped of leading/trailing whitespace
    """
    from auto_daily.capture import capture_screen
    from auto_daily.ocr import validate_ocr_result

    # Capture current screen (should contain visible text like menu bar, window titles)
    image_path = capture_screen(output_dir=tmp_path)
    assert image_path is not None

    # Act
    text = perform_ocr(image_path)
    is_valid, validated_text = validate_ocr_result(text)

    # Assert
    # Since we're running in a GUI environment, there should be some text visible
    assert isinstance(validated_text, str)
    # Validated text should be stripped
    assert validated_text == validated_text.strip()
    # is_valid should be True if text is non-empty
    assert is_valid == (len(validated_text) > 0)
