"""Configuration management for Plant Based Assistant."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    SPOONACULAR_API_KEY: str = os.getenv("SPOONACULAR_API_KEY", "")
    USDA_API_KEY: str = os.getenv("USDA_API_KEY", "")

    # LLM Configuration (using GitHub token for Copilot/GPT-4o access)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CACHE_TYPE: str = os.getenv("CACHE_TYPE", "file")
    CACHE_TTL_HOURS: int = int(os.getenv("CACHE_TTL_HOURS", "24"))

    # UI Settings
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    NATURE_THEME: bool = os.getenv("NATURE_THEME", "True").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate that required environment variables are set."""
        from utils.exceptions import ConfigurationError

        required_keys = [
            "GITHUB_TOKEN",
            "SPOONACULAR_API_KEY",
            "USDA_API_KEY",
        ]

        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key, None):
                missing_keys.append(key)

        if missing_keys:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_keys)}. "
                f"Please copy .env.example to .env and fill in the values. "
                f"GITHUB_TOKEN should be your personal access token with GPT-4o access via Copilot."
            )

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> str:
        """Get a configuration value by key."""
        return getattr(cls, key, default)


# Create global settings instance
settings = Settings()
