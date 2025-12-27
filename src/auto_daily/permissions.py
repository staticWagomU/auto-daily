"""macOS permissions checking and management module (PBI-020, PBI-046b).

This module provides functions to:
1. Check screen recording permission status
2. Check accessibility permission status
3. Check microphone permission status (PBI-046b)
4. Check speech recognition permission status (PBI-046b)
5. Open the relevant System Preferences panes
"""

import subprocess
from ctypes import CDLL, c_bool

from AVFoundation import AVAudioSession  # type: ignore[import-untyped]
from Quartz import CGPreflightScreenCaptureAccess  # type: ignore[import-untyped]
from Speech import SFSpeechRecognizer  # type: ignore[import-untyped]

# AVAudioSession record permission constants (FourCC codes)
AVAudioSessionRecordPermissionGranted = 1735552628  # 'gran'

# Load ApplicationServices framework for accessibility API
_app_services = CDLL(
    "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
)
_app_services.AXIsProcessTrusted.restype = c_bool


def AXIsProcessTrusted() -> bool:
    """Check if the process is trusted for accessibility."""
    return _app_services.AXIsProcessTrusted()


# System Preferences URLs for permission settings
SCREEN_RECORDING_URL = (
    "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
)
ACCESSIBILITY_URL = (
    "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
)


def check_screen_recording_permission() -> bool:
    """Check if screen recording permission is granted.

    Uses Quartz.CGPreflightScreenCaptureAccess() to check if the application
    has permission to capture the screen.

    Returns:
        True if permission is granted, False otherwise.
    """
    return CGPreflightScreenCaptureAccess()


def check_accessibility_permission() -> bool:
    """Check if accessibility permission is granted.

    Uses ApplicationServices.AXIsProcessTrusted() to check if the application
    has accessibility permission for window information access.

    Returns:
        True if permission is granted, False otherwise.
    """
    return AXIsProcessTrusted()


def check_microphone_permission() -> bool:
    """Check if microphone permission is granted.

    Uses AVAudioSession.sharedInstance().recordPermission to check if the
    application has permission to access the microphone.

    Returns:
        True if permission is granted, False otherwise.
        Returns False for undetermined status (conservative behavior).
    """
    session = AVAudioSession.sharedInstance()
    permission = session.recordPermission()
    return permission == AVAudioSessionRecordPermissionGranted


def check_speech_recognition_permission() -> bool:
    """Check if speech recognition permission is granted.

    Uses SFSpeechRecognizer.authorizationStatus() to check if the
    application has permission to use speech recognition.

    Returns:
        True if permission is authorized, False otherwise.
        Returns False for not determined, denied, or restricted status.
    """
    # SFSpeechRecognizerAuthorizationStatusAuthorized = 3
    status = SFSpeechRecognizer.authorizationStatus()
    return status == 3


def check_all_permissions() -> dict[str, bool]:
    """Check all required permissions and return their status.

    Returns:
        A dictionary with permission names as keys and boolean status as values.
        Keys: "screen_recording", "accessibility", "microphone", "speech_recognition"
    """
    return {
        "screen_recording": check_screen_recording_permission(),
        "accessibility": check_accessibility_permission(),
        "microphone": check_microphone_permission(),
        "speech_recognition": check_speech_recognition_permission(),
    }


def open_screen_recording_settings() -> None:
    """Open the Screen Recording settings in System Preferences."""
    subprocess.run(["open", SCREEN_RECORDING_URL], check=True)


def open_accessibility_settings() -> None:
    """Open the Accessibility settings in System Preferences."""
    subprocess.run(["open", ACCESSIBILITY_URL], check=True)


def open_permissions_settings() -> None:
    """Open both Screen Recording and Accessibility settings.

    Opens the System Preferences panes for:
    1. Screen Recording (Privacy & Security > Screen Recording)
    2. Accessibility (Privacy & Security > Accessibility)
    """
    open_screen_recording_settings()
    open_accessibility_settings()
