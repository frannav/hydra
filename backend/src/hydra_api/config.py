"""HYDRA API configuration via pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment variables and .env file."""

    # Model API
    model_api_key: str
    model_api_base_url: str = "https://model-provider.example/v1"

    # Model selection
    hydra_chat_model: str = "qwen3.6"
    hydra_review_model: str = "gemma4"
    hydra_embedding_model: str = "qwen3-embedding"

    # Langfuse tracing
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"

    # Database
    database_url: str = "postgresql+psycopg://hydra:hydra@localhost:5432/hydra"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
