"""Common capture pipeline for window monitoring and periodic capture."""

from dataclasses import dataclass
from pathlib import Path

from auto_daily.capture import capture_screen, cleanup_image
from auto_daily.logger import append_log_hourly
from auto_daily.ocr import perform_ocr
from auto_daily.slack_parser import SlackContext, parse_slack_title


@dataclass
class CaptureContext:
    """Context for capture pipeline execution.

    Attributes:
        window_info: Window information (app_name, window_title).
        log_dir: Directory for storing logs and temporary captures.
        extract_slack_context: Whether to extract Slack context from window title.
    """

    window_info: dict[str, str]
    log_dir: Path
    extract_slack_context: bool = False


def execute_capture_pipeline(context: CaptureContext) -> bool:
    """Execute the capture pipeline.

    Captures the screen, performs OCR, logs the activity, and cleans up.

    Args:
        context: Capture context containing window info and configuration.

    Returns:
        True if processing completed successfully, False otherwise.
    """
    image_path = capture_screen(context.log_dir)
    if image_path is None:
        return False

    ocr_text = perform_ocr(image_path)

    slack_context: SlackContext | None = None
    if context.extract_slack_context and context.window_info.get("app_name") == "Slack":
        slack_context = parse_slack_title(context.window_info.get("window_title", ""))

    append_log_hourly(
        context.log_dir, context.window_info, ocr_text, slack_context=slack_context
    )

    cleanup_image(image_path)

    return True
