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
