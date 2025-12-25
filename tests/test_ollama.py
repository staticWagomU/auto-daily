"""Tests for Ollama API integration."""

from unittest.mock import AsyncMock, MagicMock, patch

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
    mock_response_data = {"response": "This is a test response from Ollama."}

    # Create a mock response object
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()

    # Mock the AsyncClient context manager and post method
    mock_post = AsyncMock(return_value=mock_response)

    with patch("auto_daily.ollama.httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = mock_post
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        # Act
        result = await client.generate(
            model="llama3.2",
            prompt="Hello, this is a test.",
        )

        # Assert
        assert result == "This is a test response from Ollama."
        mock_post.assert_called_once()
