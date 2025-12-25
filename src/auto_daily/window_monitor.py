"""Window monitoring module for macOS."""

import subprocess
from collections.abc import Callable

type WindowInfo = dict[str, str]
type WindowChangeCallback = Callable[[WindowInfo, WindowInfo], None]


def get_active_window() -> dict[str, str]:
    """Get the currently active window's app name and window title using AppleScript.

    Returns:
        dict with 'app_name' and 'window_title' keys.
    """
    script = """
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set appName to name of frontApp
        try
            set windowTitle to name of first window of frontApp
        on error
            set windowTitle to ""
        end try
    end tell
    return appName & "|||" & windowTitle
    """

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout.strip()
    parts = output.split("|||")

    return {
        "app_name": parts[0] if len(parts) > 0 else "",
        "window_title": parts[1] if len(parts) > 1 else "",
    }


class WindowMonitor:
    """Monitor window changes and trigger callbacks when the active window changes."""

    def __init__(self, on_window_change: WindowChangeCallback) -> None:
        """Initialize the window monitor.

        Args:
            on_window_change: Callback function called when window changes.
                              Receives (old_window, new_window) as arguments.
        """
        self._on_window_change = on_window_change
        self._current_window: WindowInfo | None = None

    def _check_window_change(self, new_window: WindowInfo) -> None:
        """Check if window has changed and trigger callback if so.

        Args:
            new_window: The new window information to compare against current.
        """
        if self._current_window is not None and self._current_window != new_window:
            self._on_window_change(self._current_window, new_window)
        self._current_window = new_window
