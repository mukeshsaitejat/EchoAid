"""
EchoAid configuration.

All runtime settings are read from environment variables or a .env file.
Copy .env.example to .env and fill in values before starting the server.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    # Guardian auth
    guardian_pin: str = "1234"
    secret_key: str = "change-me-in-production"
    session_expire_minutes: int = 480

    # AI provider (Groq — OpenAI-compatible)
    ai_provider_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "llama-3.1-8b-instant"
    ai_api_key: str = ""
    ai_max_tokens: int = 300
    ai_timeout_seconds: int = 15

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in ("development", "testing")

    @property
    def ai_configured(self) -> bool:
        """True only when both the URL and API key are set."""
        return bool(self.ai_provider_url and self.ai_api_key)


settings = Settings()
