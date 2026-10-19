"""
EchoAid configuration.

All runtime settings are read from environment variables.
Copy .env.example to .env and fill in values before starting the server.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings resolved from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_env: str = "development"

    # Database
    database_url: str = "sqlite:///./echoaid.db"

    # Guardian (Phase 2)
    guardian_pin: str = "1234"
    secret_key: str = "change-me-in-production"

    # AI provider (Phase 4)
    ai_provider_url: str = ""
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_max_tokens: int = 256
    ai_timeout_seconds: int = 15

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @property
    def ai_configured(self) -> bool:
        """True only when the AI provider URL and API key are both set."""
        return bool(self.ai_provider_url and self.ai_api_key)


# Module-level singleton — import this throughout the backend.
settings = Settings()
