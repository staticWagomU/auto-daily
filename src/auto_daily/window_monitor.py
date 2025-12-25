"""Window monitoring module for macOS."""

import subprocess


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
