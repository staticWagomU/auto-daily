"""Window change processing pipeline."""

from pathlib import Path

from auto_daily.capture_pipeline import CaptureContext, execute_capture_pipeline


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
    context = CaptureContext(
        window_info=new_window,
        log_dir=log_dir,
        extract_slack_context=True,
    )
    return execute_capture_pipeline(context)
