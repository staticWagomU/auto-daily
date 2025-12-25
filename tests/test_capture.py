"""Tests for screen capture functionality."""

import os
from pathlib import Path

from auto_daily.capture import capture_screen


def test_screen_capture(tmp_path: Path) -> None:
    """Test that capture_screen captures the screen and returns a valid image path.

    The function should:
    1. Capture the screen using macOS screencapture command
    2. Save the image to the specified directory
    3. Return the path to the captured image
    4. The file should exist and be a valid image
    """
    # Act
    image_path = capture_screen(output_dir=tmp_path)

    # Assert
    assert image_path is not None
    assert Path(image_path).exists()
    assert Path(image_path).suffix == ".png"
    assert os.path.getsize(image_path) > 0
