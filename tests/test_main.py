"""Tests for main entrypoint."""

import subprocess
import sys


def test_module_execution() -> None:
    """Test that python -m auto_daily runs successfully.

    The module should:
    1. Be executable via python -m auto_daily
    2. Exit with code 0 on normal termination
    3. Import and call the main() function
    """
    # Act: Run the module with --help or a quick exit flag
    # We use a timeout to avoid hanging if the app starts monitoring
    result = subprocess.run(
        [sys.executable, "-m", "auto_daily", "--help"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    # Assert: Should exit cleanly (0) or show help/usage
    # --help typically exits with 0
    assert result.returncode == 0
    assert "auto-daily" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_cli_entrypoint() -> None:
    """Test that auto-daily command works via pyproject.toml scripts.

    The CLI should:
    1. Be callable via the 'auto-daily' command after pip install
    2. Support --help flag
    3. Show usage information
    """
    # Act: Import and call main directly (simulates CLI invocation)
    from auto_daily import main

    # Verify main is callable
    assert callable(main)

    # Test via subprocess with the scripts entry point
    # This requires the package to be installed in editable mode
    result = subprocess.run(
        [sys.executable, "-c", "from auto_daily import main; main()"],
        input="",
        capture_output=True,
        text=True,
        timeout=5,
        env={**dict(__import__("os").environ), "COLUMNS": "80"},
    )

    # When called without args, should print version and exit normally
    assert result.returncode == 0
    assert "auto-daily" in result.stdout.lower()


def test_main_starts_monitoring() -> None:
    """Test that main() starts the window monitoring loop when --start is passed.

    The main function should:
    1. Accept a --start flag to begin monitoring
    2. Create a WindowMonitor instance
    3. Call WindowMonitor.start() to begin the monitoring loop
    """
    from unittest.mock import MagicMock, patch

    # Arrange: Mock WindowMonitor to avoid actual monitoring
    mock_monitor_instance = MagicMock()
    mock_monitor_class = MagicMock(return_value=mock_monitor_instance)

    with (
        patch("auto_daily.WindowMonitor", mock_monitor_class),
        patch("sys.argv", ["auto-daily", "--start"]),
        patch("time.sleep", side_effect=KeyboardInterrupt),  # Stop loop immediately
    ):
        from auto_daily import main

        # Act: Call main with --start
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            pass  # Expected when we interrupt the loop

    # Assert: WindowMonitor should have been instantiated and started
    mock_monitor_class.assert_called_once()
    mock_monitor_instance.start.assert_called_once()
