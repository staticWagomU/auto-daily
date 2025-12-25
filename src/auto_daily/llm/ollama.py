"""Ollama LLM client implementation."""

import httpx

from auto_daily.config import get_ollama_base_url


def check_ollama_connection(base_url: str | None = None) -> bool:
    """Check if Ollama server is available.

    Args:
        base_url: Base URL of the Ollama server.
                 Uses OLLAMA_BASE_URL env var or default if not specified.

    Returns:
        True if Ollama is available, False otherwise.
    """
    url = base_url if base_url is not None else get_ollama_base_url()
    try:
        response = httpx.get(f"{url}/api/tags", timeout=5.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
        return False


class OllamaClient:
    """Client for interacting with the Ollama API.

    Implements the LLMClient protocol for use with the LLM abstraction layer.
    """

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize the Ollama client.

        Args:
            base_url: Base URL of the Ollama server.
                     Uses OLLAMA_BASE_URL env var or default if not specified.
        """
        self.base_url = base_url if base_url is not None else get_ollama_base_url()

    async def generate(self, prompt: str, model: str) -> str:
        """Generate text using the Ollama API.

        Args:
            prompt: The prompt to send to the model.
            model: Name of the model to use.

        Returns:
            Generated text response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["response"]
