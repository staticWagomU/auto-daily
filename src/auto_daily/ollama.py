"""Ollama API integration for daily report generation."""


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
        raise NotImplementedError("generate is not yet implemented")
