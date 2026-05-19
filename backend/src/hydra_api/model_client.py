"""HYDRA API — Model client wrapper.

Provides a thin wrapper around an OpenAI-compatible API,
a chat-model factory, and a chain builder.
Reads MODEL_API_KEY and MODEL_API_BASE_URL from configuration.
Does not make any calls at import time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from openai import AsyncOpenAI

from hydra_api.config import get_settings

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


def create_model_client() -> AsyncOpenAI:
    """Create and return an AsyncOpenAI client configured from Settings.

    The client is lazy — no network calls are made until a method is invoked.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.model_api_key,
        base_url=settings.model_api_base_url,
    )


def create_chat_model(
    model_name: str | None = None,
    settings: Any | None = None,
) -> "BaseChatModel":
    """Create a chat model instance configured from Settings.

    Parameters
    ----------
    model_name : str | None
        The model name to use.  When ``None``, defaults to
        ``settings.hydra_chat_model``.
    settings : Settings | None
        Optional Settings instance.  When ``None``, ``get_settings()``
        is called inside this function.

    Returns
    -------
    BaseChatModel
        A configured chat model ready for use.
    """
    # Lazy import to avoid import-time side effects.
    from langchain_openai import ChatOpenAI

    if settings is None:
        settings = get_settings()

    if model_name is None:
        model_name = settings.hydra_chat_model

    return ChatOpenAI(
        model=model_name,
        api_key=settings.model_api_key,
        base_url=settings.model_api_base_url,
    )


def build_chain(
    prompt_builder: Callable | None = None,
    model_name: str | None = None,
) -> Callable[[str], str]:
    """Build a LangChain LCEL chain for a given model.

    Creates a ``ChatOpenAI`` instance and wraps it with a simple
    ``RunnableLambda`` that extracts the answer text from the
    model response.

    Parameters
    ----------
    prompt_builder : callable | None
        Optional callable ``(prompt: str) -> str`` that transforms
        the raw prompt before sending to the model.  When ``None``,
        the raw prompt is passed through unchanged.
    model_name : str | None
        The model name to use.  When ``None``, defaults to
        ``settings.hydra_chat_model``.

    Returns
    -------
    callable
        A callable that accepts a prompt string and returns the
        model's response as a string.
    """
    # Lazy imports to avoid import-time side effects.
    from langchain_core.runnables import RunnableLambda

    chat_model = create_chat_model(model_name=model_name)

    def extract_answer(response: Any) -> str:
        """Extract the answer text from a model response."""
        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

    chain = chat_model | RunnableLambda(extract_answer)

    if prompt_builder is not None:
        chain = prompt_builder | chain  # type: ignore[operator]

    return chain
