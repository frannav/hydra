"""HYDRA API — Model client wrapper.

Provides a thin wrapper around an OpenAI-compatible API.
Reads MODEL_API_KEY and MODEL_API_BASE_URL from configuration.
Does not make any calls at import time.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from hydra_api.config import get_settings


def create_model_client() -> AsyncOpenAI:
    """Create and return an AsyncOpenAI client configured from Settings.

    The client is lazy — no network calls are made until a method is invoked.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.model_api_key,
        base_url=settings.model_api_base_url,
    )
