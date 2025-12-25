"""Screen capture module for macOS."""

import subprocess
import uuid
from pathlib import Path


def capture_screen(output_dir: Path) -> str | None:
    """Capture the screen and save it as an image.

    Args:
        output_dir: Directory where the captured image will be saved.

    Returns:
        Path to the captured image file, or None if capture failed.
    """
    filename = f"capture_{uuid.uuid4().hex}.png"
    output_path = output_dir / filename

    try:
        subprocess.run(
            ["screencapture", "-x", "-C", str(output_path)],
            check=True,
            capture_output=True,
        )
        if output_path.exists():
            return str(output_path)
        return None
    except subprocess.CalledProcessError:
        return None
