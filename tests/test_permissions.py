"""Tests for macOS permissions module (PBI-020)."""

from unittest.mock import MagicMock, patch

# ============================================================
# ST-001: check_screen_recording_permission
# ============================================================


def test_check_screen_recording_permission_granted() -> None:
    """Test that screen recording permission check returns True when granted.

    The function should:
    1. Use Quartz.CGPreflightScreenCaptureAccess() to check permission
    2. Return True when the permission is granted
    """
    from auto_daily.permissions import check_screen_recording_permission

    # Arrange: Mock CGPreflightScreenCaptureAccess to return True
    with patch(
        "auto_daily.permissions.CGPreflightScreenCaptureAccess", return_value=True
    ):
        # Act: Check permission
        result = check_screen_recording_permission()

        # Assert: Should return True
        assert result is True


def test_check_screen_recording_permission_denied() -> None:
    """Test that screen recording permission check returns False when denied.

    The function should:
    1. Use Quartz.CGPreflightScreenCaptureAccess() to check permission
    2. Return False when the permission is denied
    """
    from auto_daily.permissions import check_screen_recording_permission

    # Arrange: Mock CGPreflightScreenCaptureAccess to return False
    with patch(
        "auto_daily.permissions.CGPreflightScreenCaptureAccess", return_value=False
    ):
        # Act: Check permission
        result = check_screen_recording_permission()

        # Assert: Should return False
        assert result is False


# ============================================================
# ST-002: check_accessibility_permission
# ============================================================


def test_check_accessibility_permission_granted() -> None:
    """Test that accessibility permission check returns True when granted.

    The function should:
    1. Use ApplicationServices.AXIsProcessTrusted() to check permission
    2. Return True when the permission is granted
    """
    from auto_daily.permissions import check_accessibility_permission

    # Arrange: Mock AXIsProcessTrusted to return True
    with patch("auto_daily.permissions.AXIsProcessTrusted", return_value=True):
        # Act: Check permission
        result = check_accessibility_permission()

        # Assert: Should return True
        assert result is True


def test_check_accessibility_permission_denied() -> None:
    """Test that accessibility permission check returns False when denied.

    The function should:
    1. Use ApplicationServices.AXIsProcessTrusted() to check permission
    2. Return False when the permission is denied
    """
    from auto_daily.permissions import check_accessibility_permission

    # Arrange: Mock AXIsProcessTrusted to return False
    with patch("auto_daily.permissions.AXIsProcessTrusted", return_value=False):
        # Act: Check permission
        result = check_accessibility_permission()

        # Assert: Should return False
        assert result is False


# ============================================================
# ST-003: check_all_permissions
# ============================================================


def test_check_all_permissions_all_granted() -> None:
    """Test that check_all_permissions returns correct status when all granted.

    The function should:
    1. Check both screen recording and accessibility permissions
    2. Return a dictionary with permission names as keys and booleans as values
    """
    from auto_daily.permissions import check_all_permissions

    # Arrange: Mock both permission checks to return True
    with (
        patch(
            "auto_daily.permissions.check_screen_recording_permission",
            return_value=True,
        ),
        patch(
            "auto_daily.permissions.check_accessibility_permission", return_value=True
        ),
    ):
        # Act: Check all permissions
        result = check_all_permissions()

        # Assert: Should return dict with all True
        assert result == {"screen_recording": True, "accessibility": True}


def test_check_all_permissions_none_granted() -> None:
    """Test that check_all_permissions returns correct status when none granted.

    The function should:
    1. Check both permissions
    2. Return a dictionary with False for denied permissions
    """
    from auto_daily.permissions import check_all_permissions

    # Arrange: Mock both permission checks to return False
    with (
        patch(
            "auto_daily.permissions.check_screen_recording_permission",
            return_value=False,
        ),
        patch(
            "auto_daily.permissions.check_accessibility_permission", return_value=False
        ),
    ):
        # Act: Check all permissions
        result = check_all_permissions()

        # Assert: Should return dict with all False
        assert result == {"screen_recording": False, "accessibility": False}


def test_check_all_permissions_partial() -> None:
    """Test that check_all_permissions returns correct status when partially granted.

    The function should correctly report mixed permission states.
    """
    from auto_daily.permissions import check_all_permissions

    # Arrange: Mock screen recording granted, accessibility denied
    with (
        patch(
            "auto_daily.permissions.check_screen_recording_permission",
            return_value=True,
        ),
        patch(
            "auto_daily.permissions.check_accessibility_permission", return_value=False
        ),
    ):
        # Act: Check all permissions
        result = check_all_permissions()

        # Assert: Should return dict with mixed status
        assert result == {"screen_recording": True, "accessibility": False}


# ============================================================
# ST-004: open_permissions_settings
# ============================================================


def test_open_permissions_settings() -> None:
    """Test that open_permissions_settings opens the correct system preferences.

    The function should:
    1. Use subprocess to open Screen Recording settings
    2. Use subprocess to open Accessibility settings
    3. Use the correct x-apple.systempreferences URLs
    """
    from auto_daily.permissions import open_permissions_settings

    # Arrange: Mock subprocess.run
    mock_run = MagicMock()
    with patch("auto_daily.permissions.subprocess.run", mock_run):
        # Act: Open permissions settings
        open_permissions_settings()

        # Assert: Should call subprocess.run twice with open command
        assert mock_run.call_count == 2

        # Check that correct URLs were opened
        calls = mock_run.call_args_list
        urls_opened = [call[0][0] for call in calls]

        # Should open screen recording and accessibility settings
        assert any("Privacy_ScreenCapture" in str(url) for url in urls_opened), (
            "Screen Recording settings not opened"
        )
        assert any("Privacy_Accessibility" in str(url) for url in urls_opened), (
            "Accessibility settings not opened"
        )


def test_open_screen_recording_settings() -> None:
    """Test that open_screen_recording_settings opens Screen Recording preferences.

    The function should:
    1. Use subprocess to open the specific Screen Recording settings
    2. Use the correct x-apple.systempreferences URL
    """
    from auto_daily.permissions import open_screen_recording_settings

    # Arrange: Mock subprocess.run
    mock_run = MagicMock()
    with patch("auto_daily.permissions.subprocess.run", mock_run):
        # Act: Open screen recording settings
        open_screen_recording_settings()

        # Assert: Should call subprocess.run with correct URL
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "open" in call_args
        assert "Privacy_ScreenCapture" in str(call_args)


def test_open_accessibility_settings() -> None:
    """Test that open_accessibility_settings opens Accessibility preferences.

    The function should:
    1. Use subprocess to open the specific Accessibility settings
    2. Use the correct x-apple.systempreferences URL
    """
    from auto_daily.permissions import open_accessibility_settings

    # Arrange: Mock subprocess.run
    mock_run = MagicMock()
    with patch("auto_daily.permissions.subprocess.run", mock_run):
        # Act: Open accessibility settings
        open_accessibility_settings()

        # Assert: Should call subprocess.run with correct URL
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "open" in call_args
        assert "Privacy_Accessibility" in str(call_args)
