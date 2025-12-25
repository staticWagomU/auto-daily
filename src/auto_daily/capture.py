"""Screen capture module for macOS."""

from pathlib import Path


def capture_screen(output_dir: Path) -> str | None:
    """Capture the screen and save it as an image.

    Args:
        output_dir: Directory where the captured image will be saved.

    Returns:
        Path to the captured image file, or None if capture failed.
    """
    raise NotImplementedError("capture_screen is not yet implemented")
