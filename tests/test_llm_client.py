"""Tests for LLM client abstraction layer."""

import os
from typing import Any
from unittest.mock import patch

import pytest

from auto_daily.llm.lm_studio import LMStudioClient
from auto_daily.llm.ollama import OllamaClient
from auto_daily.llm.openai import OpenAIClient
from auto_daily.llm.protocol import LLMClient


def test_llm_protocol() -> None:
    """Test that LLMClient Protocol defines the generate() method.

    The Protocol should:
    1. Define an async generate(prompt: str, model: str) -> str method
    2. Be a valid typing.Protocol
    3. Allow structural subtyping (duck typing with type safety)
    """
    from typing import Protocol

    # Verify Protocol exists and has expected attributes
    assert hasattr(LLMClient, "generate")

    # Verify it's a Protocol class
    assert issubclass(LLMClient, Protocol)


@pytest.mark.parametrize(
    ("client_class", "init_kwargs"),
    [
        (OllamaClient, {}),
        (OpenAIClient, {"api_key": "test-api-key"}),
        (LMStudioClient, {}),
    ],
    ids=["ollama", "openai", "lm_studio"],
)
def test_client_implements_protocol(
    client_class: type, init_kwargs: dict[str, Any]
) -> None:
    """Test that LLM clients implement the LLMClient protocol.

    Each client should:
    1. Have an async generate(prompt: str, model: str) -> str method
    2. Be structurally compatible with LLMClient Protocol
    """
    # Create an instance
    client = client_class(**init_kwargs)

    # Verify the method signature exists
    assert hasattr(client, "generate")
    assert callable(client.generate)

    # Type checking verification (this is for runtime, static checking happens via mypy/ty)
    # The client should be usable where LLMClient is expected
    def accepts_llm_client(c: LLMClient) -> None:
        pass

    # This should not raise - if the client implements the protocol correctly
    accepts_llm_client(client)


def test_get_llm_client_factory() -> None:
    """Test that get_llm_client() returns the correct client based on AI_BACKEND.

    The factory should:
    1. Return OllamaClient when AI_BACKEND is "ollama" or not set
    2. Raise ValueError for unknown backends
    """
    from auto_daily.llm import get_llm_client
    from auto_daily.llm.ollama import OllamaClient

    # Test default (ollama)
    env_without_var = {k: v for k, v in os.environ.items() if k != "AI_BACKEND"}
    with patch.dict(os.environ, env_without_var, clear=True):
        client = get_llm_client()
        assert isinstance(client, OllamaClient)

    # Test explicit ollama
    with patch.dict(os.environ, {"AI_BACKEND": "ollama"}):
        client = get_llm_client()
        assert isinstance(client, OllamaClient)

    # Test unknown backend raises ValueError
    with patch.dict(os.environ, {"AI_BACKEND": "unknown_backend"}):
        with pytest.raises(ValueError, match="Unknown AI backend"):
            get_llm_client()


def test_openai_backend() -> None:
    """Test that AI_BACKEND=openai returns OpenAIClient.

    The factory should:
    1. Return OpenAIClient when AI_BACKEND is "openai"
    2. Pass through the API key to the client
    """
    from auto_daily.llm import get_llm_client
    from auto_daily.llm.openai import OpenAIClient

    with patch.dict(os.environ, {"AI_BACKEND": "openai", "OPENAI_API_KEY": "test-key"}):
        client = get_llm_client()
        assert isinstance(client, OpenAIClient)


class TestCheckOllamaConnection:
    """Tests for check_ollama_connection() function."""

    def test_check_ollama_connection_success(self) -> None:
        """Test that check_ollama_connection returns True when Ollama is available.

        The function should:
        1. Send a GET request to OLLAMA_BASE_URL/api/tags
        2. Return True when the request succeeds
        """
        from unittest.mock import MagicMock

        import httpx

        from auto_daily.llm.ollama import check_ollama_connection

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(httpx, "get", return_value=mock_response):
            result = check_ollama_connection()
            assert result is True

    def test_check_ollama_connection_failure(self) -> None:
        """Test that check_ollama_connection returns False when Ollama is unavailable.

        The function should:
        1. Return False when the connection fails (timeout, connection error, etc.)
        """
        import httpx

        from auto_daily.llm.ollama import check_ollama_connection

        with patch.object(
            httpx, "get", side_effect=httpx.ConnectError("Connection refused")
        ):
            result = check_ollama_connection()
            assert result is False

    def test_check_ollama_connection_uses_configured_url(self) -> None:
        """Test that check_ollama_connection uses the configured OLLAMA_BASE_URL.

        The function should:
        1. Use the URL from get_ollama_base_url()
        2. Append /api/tags to the base URL
        """
        from unittest.mock import MagicMock

        import httpx

        from auto_daily.llm.ollama import check_ollama_connection

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://custom:8080"}):
            with patch.object(httpx, "get", return_value=mock_response) as mock_get:
                check_ollama_connection()
                mock_get.assert_called_once()
                call_args = mock_get.call_args
                assert "http://custom:8080/api/tags" in str(call_args)


def test_lm_studio_backend() -> None:
    """Test that AI_BACKEND=lm_studio returns LMStudioClient.

    The factory should:
    1. Return LMStudioClient when AI_BACKEND is "lm_studio"
    """
    from auto_daily.llm import get_llm_client
    from auto_daily.llm.lm_studio import LMStudioClient

    with patch.dict(os.environ, {"AI_BACKEND": "lm_studio"}):
        client = get_llm_client()
        assert isinstance(client, LMStudioClient)
