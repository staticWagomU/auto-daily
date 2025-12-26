"""Window change processing pipeline."""

from pathlib import Path

from auto_daily.capture import capture_screen, cleanup_image
from auto_daily.logger import append_log_hourly
from auto_daily.ocr import perform_ocr
from auto_daily.slack_parser import SlackContext, parse_slack_title


def process_window_change(
    old_window: dict[str, str],
    new_window: dict[str, str],
    log_dir: Path,
) -> bool:
    """Process a window change event.

    Captures the screen, performs OCR, logs the activity, and cleans up.

    Args:
        old_window: Previous window information (app_name, window_title).
        new_window: New window information (app_name, window_title).
        log_dir: Directory for storing logs and temporary captures.

    Returns:
        True if processing completed successfully, False otherwise.
    """
    image_path = capture_screen(log_dir)
    if image_path is None:
        return False

    ocr_text = perform_ocr(image_path)

    slack_context: SlackContext | None = None
    if new_window.get("app_name") == "Slack":
        slack_context = parse_slack_title(new_window.get("window_title", ""))

    append_log_hourly(log_dir, new_window, ocr_text, slack_context=slack_context)

    cleanup_image(image_path)

    return True
