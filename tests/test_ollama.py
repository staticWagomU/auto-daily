"""Tests for Ollama API integration."""

from unittest.mock import AsyncMock, patch

import pytest

from auto_daily.ollama import OllamaClient


@pytest.mark.asyncio
async def test_scheduled_call() -> None:
    """Test that OllamaClient can call the Ollama API.

    The function should:
    1. Send a request to the Ollama API endpoint
    2. Return the generated response text
    3. Handle connection errors gracefully
    """
    # Arrange
    client = OllamaClient(base_url="http://localhost:11434")
    mock_response = {"response": "This is a test response from Ollama."}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200

        # Act
        result = await client.generate(
            model="llama3.2",
            prompt="Hello, this is a test.",
        )

        # Assert
        assert result == "This is a test response from Ollama."
        mock_post.assert_called_once()
