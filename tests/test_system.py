"""Tests for system state detection."""

from unittest.mock import patch

from auto_daily.system import is_screen_locked, is_system_active


class TestSystemState:
    """Test system state detection functionality."""

    @patch("auto_daily.system.CGSessionCopyCurrentDictionary")
    def test_is_screen_locked_true(self, mock_copy_dict):
        """Verify is_screen_locked returns True when screen is locked."""
        mock_copy_dict.return_value = {"CGSSessionScreenIsLocked": 1}
        assert is_screen_locked() is True

    @patch("auto_daily.system.CGSessionCopyCurrentDictionary")
    def test_is_screen_locked_false(self, mock_copy_dict):
        """Verify is_screen_locked returns False when screen is unlocked."""
        mock_copy_dict.return_value = {"CGSSessionScreenIsLocked": 0}
        assert is_screen_locked() is False

    @patch("auto_daily.system.CGSessionCopyCurrentDictionary")
    def test_is_screen_locked_missing(self, mock_copy_dict):
        """Verify is_screen_locked returns False when key is missing."""
        mock_copy_dict.return_value = {"SomeOtherKey": 1}
        assert is_screen_locked() is False

    @patch("auto_daily.system.CGSessionCopyCurrentDictionary")
    def test_is_screen_locked_none(self, mock_copy_dict):
        """Verify is_screen_locked returns False when dictionary is None."""
        mock_copy_dict.return_value = None
        assert is_screen_locked() is False

    @patch("auto_daily.system.is_screen_locked")
    def test_is_system_active_true(self, mock_locked):
        """Verify is_system_active returns True when not locked."""
        mock_locked.return_value = False
        assert is_system_active() is True

    @patch("auto_daily.system.is_screen_locked")
    def test_is_system_active_false(self, mock_locked):
        """Verify is_system_active returns False when locked."""
        mock_locked.return_value = True
        assert is_system_active() is False
