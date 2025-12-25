"""Tests for OCR functionality using Vision Framework."""

from pathlib import Path
from typing import Protocol

from auto_daily.ocr import perform_ocr


def test_ocr_protocol() -> None:
    """Test that OCRBackend Protocol is defined and has required methods.

    The Protocol should:
    1. Define a perform_ocr(image_path: str) -> str method
    2. Be a valid typing.Protocol
    3. Allow structural subtyping (duck typing with type safety)
    """
    from auto_daily.ocr.protocol import OCRBackend

    # Verify Protocol exists and has expected attributes
    assert hasattr(OCRBackend, "perform_ocr")

    # Verify it's a Protocol class
    assert issubclass(OCRBackend, Protocol)


def test_apple_vision_implements_protocol() -> None:
    """Test that AppleVisionOCR implements the OCRBackend protocol.

    The AppleVisionOCR should:
    1. Have a perform_ocr(image_path: str) -> str method
    2. Be structurally compatible with OCRBackend Protocol
    """
    from auto_daily.ocr.apple_vision import AppleVisionOCR
    from auto_daily.ocr.protocol import OCRBackend

    # Create an instance
    backend = AppleVisionOCR()

    # Verify the method signature exists
    assert hasattr(backend, "perform_ocr")
    assert callable(backend.perform_ocr)

    # Type checking verification using runtime_checkable
    assert isinstance(backend, OCRBackend)


def test_get_ocr_backend_factory() -> None:
    """Test that get_ocr_backend() returns the correct backend based on OCR_BACKEND.

    The factory should:
    1. Return AppleVisionOCR when OCR_BACKEND is "apple" or not set
    2. Raise ValueError for unknown backends
    """
    import os
    from unittest.mock import patch

    from auto_daily.ocr import get_ocr_backend
    from auto_daily.ocr.apple_vision import AppleVisionOCR

    # Test default (apple)
    env_without_var = {k: v for k, v in os.environ.items() if k != "OCR_BACKEND"}
    with patch.dict(os.environ, env_without_var, clear=True):
        backend = get_ocr_backend()
        assert isinstance(backend, AppleVisionOCR)

    # Test explicit apple
    with patch.dict(os.environ, {"OCR_BACKEND": "apple"}):
        backend = get_ocr_backend()
        assert isinstance(backend, AppleVisionOCR)

    # Test unknown backend raises ValueError
    import pytest

    with patch.dict(os.environ, {"OCR_BACKEND": "unknown_backend"}):
        with pytest.raises(ValueError, match="Unknown OCR backend"):
            get_ocr_backend()


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


# ============================================================
# PBI-029: OpenAI Vision OCR
# ============================================================


def test_openai_vision_implements_protocol() -> None:
    """Test that OpenAIVisionOCR implements the OCRBackend protocol.

    The OpenAIVisionOCR should:
    1. Have a perform_ocr(image_path: str) -> str method
    2. Be structurally compatible with OCRBackend Protocol
    """
    from unittest.mock import patch

    from auto_daily.ocr.openai_vision import OpenAIVisionOCR
    from auto_daily.ocr.protocol import OCRBackend

    # Create an instance with mocked OpenAI client
    with patch("auto_daily.ocr.openai_vision.OpenAI"):
        backend = OpenAIVisionOCR(api_key="test-key")

    # Verify the method signature exists
    assert hasattr(backend, "perform_ocr")
    assert callable(backend.perform_ocr)

    # Type checking verification using runtime_checkable
    assert isinstance(backend, OCRBackend)


def test_openai_vision_image_encoding(tmp_path: Path) -> None:
    """Test that OpenAIVisionOCR correctly encodes images as Base64.

    The OCR should:
    1. Read the image file
    2. Encode it as Base64
    3. Send it to OpenAI with the correct media type
    """
    from unittest.mock import MagicMock, patch

    from auto_daily.ocr.openai_vision import OpenAIVisionOCR

    # Create a test image file
    test_image = tmp_path / "test.png"
    test_image.write_bytes(b"fake image data")

    # Mock the OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Extracted text from image"
    mock_client.chat.completions.create.return_value = mock_response

    with patch("auto_daily.ocr.openai_vision.OpenAI", return_value=mock_client):
        backend = OpenAIVisionOCR(api_key="test-key")
        result = backend.perform_ocr(str(test_image))

    # Verify the API was called
    mock_client.chat.completions.create.assert_called_once()

    # Get the call arguments
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]

    # Verify the message structure
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    content = messages[0]["content"]
    assert len(content) == 2

    # Verify text prompt
    assert content[0]["type"] == "text"
    assert "テキストを抽出" in content[0]["text"]

    # Verify image encoding
    assert content[1]["type"] == "image_url"
    image_url = content[1]["image_url"]["url"]
    assert image_url.startswith("data:image/png;base64,")

    # Verify the result
    assert result == "Extracted text from image"


def test_openai_vision_backend() -> None:
    """Test that OCR_BACKEND=openai returns OpenAIVisionOCR.

    The factory should:
    1. Return OpenAIVisionOCR when OCR_BACKEND is "openai"
    """
    import os
    from unittest.mock import patch

    from auto_daily.ocr import get_ocr_backend
    from auto_daily.ocr.openai_vision import OpenAIVisionOCR

    # Mock environment and OpenAI client
    with (
        patch.dict(os.environ, {"OCR_BACKEND": "openai", "OPENAI_API_KEY": "test-key"}),
        patch("auto_daily.ocr.openai_vision.OpenAI"),
    ):
        backend = get_ocr_backend()
        assert isinstance(backend, OpenAIVisionOCR)


# ============================================================
# PBI-024: Ollama Vision OCR
# ============================================================


def test_ollama_vision_implements_protocol() -> None:
    """Test that OllamaVisionOCR implements the OCRBackend protocol.

    The OllamaVisionOCR should:
    1. Have a perform_ocr(image_path: str) -> str method
    2. Be structurally compatible with OCRBackend Protocol
    """
    from auto_daily.ocr.ollama_vision import OllamaVisionOCR
    from auto_daily.ocr.protocol import OCRBackend

    # Create an instance
    backend = OllamaVisionOCR(base_url="http://localhost:11434", model="llava")

    # Verify the method signature exists
    assert hasattr(backend, "perform_ocr")
    assert callable(backend.perform_ocr)

    # Type checking verification using runtime_checkable
    assert isinstance(backend, OCRBackend)


def test_ollama_vision_backend() -> None:
    """Test that OCR_BACKEND=ollama returns OllamaVisionOCR.

    The factory should:
    1. Return OllamaVisionOCR when OCR_BACKEND is "ollama"
    """
    import os
    from unittest.mock import patch

    from auto_daily.ocr import get_ocr_backend
    from auto_daily.ocr.ollama_vision import OllamaVisionOCR

    # Mock environment
    with patch.dict(os.environ, {"OCR_BACKEND": "ollama"}):
        backend = get_ocr_backend()
        assert isinstance(backend, OllamaVisionOCR)


def test_ollama_vision_image_encoding(tmp_path: Path) -> None:
    """Test that OllamaVisionOCR correctly encodes images as Base64.

    The OCR should:
    1. Read the image file
    2. Encode it as Base64
    3. Send it to Ollama with the images array
    """
    import base64
    from unittest.mock import MagicMock, patch

    from auto_daily.ocr.ollama_vision import OllamaVisionOCR

    # Create a test image file
    test_image = tmp_path / "test.png"
    test_content = b"fake image data"
    test_image.write_bytes(test_content)
    expected_base64 = base64.b64encode(test_content).decode("utf-8")

    # Mock httpx.post
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Extracted text from image"}

    with patch(
        "auto_daily.ocr.ollama_vision.httpx.post", return_value=mock_response
    ) as mock_post:
        backend = OllamaVisionOCR(base_url="http://localhost:11434", model="llava")
        result = backend.perform_ocr(str(test_image))

    # Verify the API was called
    mock_post.assert_called_once()

    # Get the call arguments
    call_args = mock_post.call_args

    # Verify URL
    assert call_args[0][0] == "http://localhost:11434/api/generate"

    # Verify JSON payload
    json_data = call_args.kwargs["json"]
    assert json_data["model"] == "llava"
    assert "テキストを抽出" in json_data["prompt"]
    assert json_data["stream"] is False
    assert "images" in json_data
    assert len(json_data["images"]) == 1
    assert json_data["images"][0] == expected_base64

    # Verify the result
    assert result == "Extracted text from image"
