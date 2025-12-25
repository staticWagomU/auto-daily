"""Tests for Slack window title parsing."""

from auto_daily.slack_parser import parse_slack_title


class TestChannelExtraction:
    """Tests for extracting channel name from Slack window title."""

    def test_channel_extraction_with_pipe_separator(self) -> None:
        """Test channel extraction with pipe separator."""
        title = "#general | My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] == "general"

    def test_channel_extraction_with_dash_separator(self) -> None:
        """Test channel extraction with dash separator."""
        title = "#random - My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] == "random"

    def test_channel_extraction_with_hyphenated_name(self) -> None:
        """Test channel extraction with hyphenated channel name."""
        title = "#dev-team-discussions | Company Slack"
        result = parse_slack_title(title)
        assert result["channel"] == "dev-team-discussions"

    def test_dm_extraction(self) -> None:
        """Test DM user extraction."""
        title = "@john.doe | My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] is None
        assert result["dm_user"] == "john.doe"

    def test_thread_channel_extraction(self) -> None:
        """Test channel extraction from thread view."""
        title = "Thread in #general | My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] == "general"
        assert result["is_thread"] is True

    def test_non_slack_title_returns_none(self) -> None:
        """Test that non-Slack titles return None values."""
        title = "Some Random Window Title"
        result = parse_slack_title(title)
        assert result["channel"] is None
        assert result["workspace"] is None


class TestWorkspaceExtraction:
    """Tests for extracting workspace name from Slack window title."""

    def test_workspace_extraction_with_pipe_separator(self) -> None:
        """Test workspace extraction with pipe separator."""
        title = "#general | My Workspace"
        result = parse_slack_title(title)
        assert result["workspace"] == "My Workspace"

    def test_workspace_extraction_with_dash_separator(self) -> None:
        """Test workspace extraction with dash separator."""
        title = "#random - Company Slack"
        result = parse_slack_title(title)
        assert result["workspace"] == "Company Slack"

    def test_workspace_with_multiple_words(self) -> None:
        """Test workspace extraction with multiple words."""
        title = "#dev | Acme Corporation Workspace"
        result = parse_slack_title(title)
        assert result["workspace"] == "Acme Corporation Workspace"

    def test_workspace_from_dm(self) -> None:
        """Test workspace extraction from DM title."""
        title = "@alice | Team Slack"
        result = parse_slack_title(title)
        assert result["workspace"] == "Team Slack"

    def test_workspace_from_thread(self) -> None:
        """Test workspace extraction from thread title."""
        title = "Thread in #general | My Workspace"
        result = parse_slack_title(title)
        assert result["workspace"] == "My Workspace"


class TestSlackContextInLog:
    """Tests for Slack context integration with logging."""

    def test_slack_context_structure(self) -> None:
        """Test that parse_slack_title returns proper context structure."""
        title = "#general | My Workspace"
        result = parse_slack_title(title)

        assert "channel" in result
        assert "workspace" in result
        assert "dm_user" in result
        assert "is_thread" in result

    def test_slack_context_for_channel(self) -> None:
        """Test Slack context for a regular channel."""
        title = "#dev-team | Company"
        result = parse_slack_title(title)

        assert result["channel"] == "dev-team"
        assert result["workspace"] == "Company"
        assert result["dm_user"] is None
        assert result["is_thread"] is False

    def test_slack_context_for_dm(self) -> None:
        """Test Slack context for a DM."""
        title = "@bob | Company"
        result = parse_slack_title(title)

        assert result["channel"] is None
        assert result["workspace"] == "Company"
        assert result["dm_user"] == "bob"
        assert result["is_thread"] is False

    def test_slack_context_for_thread(self) -> None:
        """Test Slack context for a thread."""
        title = "Thread in #random | Company"
        result = parse_slack_title(title)

        assert result["channel"] == "random"
        assert result["workspace"] == "Company"
        assert result["dm_user"] is None
        assert result["is_thread"] is True
