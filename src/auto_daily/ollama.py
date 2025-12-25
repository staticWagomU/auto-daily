"""Ollama API integration for daily report generation."""

import httpx


class OllamaClient:
    """Client for interacting with the Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """Initialize the Ollama client.

        Args:
            base_url: Base URL of the Ollama server.
        """
        self.base_url = base_url

    async def generate(self, model: str, prompt: str) -> str:
        """Generate text using the Ollama API.

        Args:
            model: Name of the model to use.
            prompt: The prompt to send to the model.

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
