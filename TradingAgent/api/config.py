"""API configuration settings."""
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """Settings for the FastAPI dashboard API."""

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.53:3000",
    ]
    db_path: str = "trading_agent.db"
    ws_heartbeat: int = 30

    model_config = {
        "env_prefix": "TA_API_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def get_api_settings() -> APISettings:
    """Get API settings singleton."""
    return APISettings()
