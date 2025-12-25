"""Module for detecting macOS system state (sleep, lock, idle)."""

# ty: ignore - PyObjC dynamically exports this from CoreGraphics
from Quartz.CoreGraphics import (
    CGSessionCopyCurrentDictionary,  # type: ignore[attr-defined]
)


def is_screen_locked() -> bool:
    """Check if the macOS screen is locked.

    Returns:
        True if the screen is locked, False otherwise.
    """
    # CGSessionCopyCurrentDictionary returns information about the current session.
    # If the session is locked, it contains the 'CGSSessionScreenIsLocked' key.
    session_info = CGSessionCopyCurrentDictionary()
    if session_info:
        # The value is typically 1 (True) or missing/None
        return bool(session_info.get("CGSSessionScreenIsLocked"))
    return False


def is_system_active() -> bool:
    """Check if the system is currently active for the user.

    Returns:
        True if the system is active (not locked, etc.), False otherwise.
    """
    if is_screen_locked():
        return False

    return True
