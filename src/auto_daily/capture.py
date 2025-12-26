"""Screen capture module for macOS."""

import logging
import subprocess
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


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
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ["screencapture", "-x", "-C", str(output_path)],
            check=True,
            capture_output=True,
        )
        if output_path.exists():
            return str(output_path)
        # Capture command succeeded but file not created
        import sys

        print(
            f"  [debug] screencapture succeeded but file not found: {output_path}",
            file=sys.stderr,
        )
        return None
    except subprocess.CalledProcessError as e:
        import sys

        print(
            f"  [debug] screencapture failed: {e.stderr.decode() if e.stderr else e}",
            file=sys.stderr,
        )
        return None


def cleanup_image(image_path: str) -> bool:
    """Delete a captured image file.

    Args:
        image_path: Path to the image file to delete.

    Returns:
        True if the file was successfully deleted, False otherwise.
    """
    try:
        path = Path(image_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except OSError:
        return False
