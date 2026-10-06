import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """Central configuration class for CampusIQ application."""

    # API & LLM Settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Embedding Settings (Local execution)
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    # RAG Text Splitter Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))

    # Vector Retrieval Defaults
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "4"))

    # Server Settings
    PORT: int = int(os.getenv("PORT", "7860"))

    @classmethod
    def validate_api_key(cls) -> bool:
        """Check if OpenRouter API key is configured."""
        return bool(cls.OPENROUTER_API_KEY and cls.OPENROUTER_API_KEY.strip() != "" and not cls.OPENROUTER_API_KEY.startswith("your_"))

    @classmethod
    def get_masked_api_key(cls) -> str:
        """Return a safe masked version of the API key for UI display."""
        key = cls.OPENROUTER_API_KEY
        if not cls.validate_api_key():
            return "Not Configured"
        if len(key) <= 8:
            return "****"
        return f"{key[:4]}...{key[-4:]}"
