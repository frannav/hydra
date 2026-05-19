"""HYDRA API — Observability helpers and local trace fallback.

This module provides safe text helpers for truncation and redaction,
local trace ID generation, and a lazy observability emitter factory.

No .env file, no MODEL_API_KEY, and no network calls are required
at import time.
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol


# ---------------------------------------------------------------------------
# Module-level constants for safe length limits
# ---------------------------------------------------------------------------

MAX_QUESTION_PREVIEW_CHARS: int = 200
MAX_EVIDENCE_PREVIEW_CHARS: int = 500
MAX_RESPONSE_PREVIEW_CHARS: int = 300
MAX_PROMPT_VERSION: str = "1.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def safe_preview(text: str | None, max_chars: int = MAX_RESPONSE_PREVIEW_CHARS) -> str:
    """Return a truncated preview of *text*.

    - Normalises whitespace to single spaces.
    - Truncates to *max_chars* and appends ``...`` when the text is longer
      than *max_chars*, yielding a result of length ``max_chars + 3``.
    - Returns ``""`` for ``None`` or empty strings.
    - When the input is only whitespace, returns ``"..."`` (3 chars).
    """
    if text is None:
        return ""

    # Empty string returns empty string (not "...")
    if text == "":
        return ""

    # Normalise whitespace: collapse runs of whitespace to single space, strip
    normalised = re.sub(r"\s+", " ", text).strip()

    if not normalised:
        return "..."

    if len(normalised) <= max_chars:
        return normalised

    return normalised[:max_chars] + "..."


def redact_secret_like_values(value: str | None) -> str:
    """Hide values that look like secrets.

    Patterns handled:
    - ``Bearer <token>`` — the token part is replaced with ``[REDACTED]``.
    - Values starting with ``sk-`` (OpenAI-style keys) — the key part
      after ``sk-`` is replaced with ``[REDACTED]``.

    Returns the original value unchanged when no pattern matches.
    Returns ``""`` when *value* is ``None``.
    """
    if value is None:
        return ""

    # Bearer token
    bearer_match = re.match(r"(Bearer\s+)(\S+)", value)
    if bearer_match:
        return bearer_match.group(1) + "[REDACTED]"

    # sk-... style keys
    sk_match = re.match(r"(sk-)(\S+)", value)
    if sk_match:
        return sk_match.group(1) + "[REDACTED]"

    return value


# ---------------------------------------------------------------------------
# Local trace ID generation
# ---------------------------------------------------------------------------


def generate_local_trace_id() -> str:
    """Return a unique ``local-`` prefixed trace ID.

    The ID is guaranteed to:
    - Start with ``local-``.
    - Contain no spaces, forward slashes, backslashes, or ``..``.
    - Be unique per call (UUID4 entropy).
    """
    return f"local-{uuid.uuid4().hex}"


# ---------------------------------------------------------------------------
# TraceContext
# ---------------------------------------------------------------------------


@dataclass
class TraceContext:
    """A single trace context with metadata and timing helper."""

    trace_id: str
    name: str
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)

    def duration(self) -> float:
        """Return elapsed seconds since this trace was started."""
        return time.time() - self.started_at


# ---------------------------------------------------------------------------
# Local trace helpers (pure functions, no network)
# ---------------------------------------------------------------------------


def start_local_trace(
    name: str,
    metadata: dict[str, Any] | None = None,
) -> TraceContext:
    """Start a local trace and return a :class:`TraceContext`.

    *metadata* is deep-copied so concurrent traces never share mutable state.
    """
    return TraceContext(
        trace_id=generate_local_trace_id(),
        name=name,
        metadata=dict(metadata) if metadata is not None else {},
    )


def close_local_trace(context: TraceContext) -> float:
    """Close a local trace and return its duration in seconds."""
    return context.duration()


# ---------------------------------------------------------------------------
# ObservabilityEmitter protocol
# ---------------------------------------------------------------------------


class ObservabilityEmitter(Protocol):
    """Protocol for observability emitters.

    Implementations may be Langfuse-backed or local/no-op.
    """

    def start_trace(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> TraceContext: ...

    def event(
        self,
        trace_id: str,
        event_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

    def score(
        self,
        trace_id: str,
        name: str,
        value: float | int | str | bool,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...


# ---------------------------------------------------------------------------
# Local (no-op) emitter
# ---------------------------------------------------------------------------


class _LocalEmitter:
    """A no-op emitter that uses local trace IDs."""

    def start_trace(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> TraceContext:
        return start_local_trace(name, metadata)

    def event(
        self,
        trace_id: str,
        event_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pass

    def score(
        self,
        trace_id: str,
        name: str,
        value: float | int | str | bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pass


# ---------------------------------------------------------------------------
# Emitter factory (lazy — no client created at import time)
# ---------------------------------------------------------------------------


class _SettingsLike:
    """Minimal duck-type for settings passed to the factory."""

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = ""


def create_observability_emitter(
    settings: Any | None = None,
) -> ObservabilityEmitter:
    """Create an observability emitter.

    - When *langfuse_public_key* and *langfuse_secret_key* are both
      non-empty, attempts to create a Langfuse-backed emitter.
    - When either key is missing or empty, returns a local no-op emitter.

    This function never raises and never imports Langfuse at module level.
    """
    public_key = ""
    secret_key = ""

    if settings is not None:
        public_key = getattr(settings, "langfuse_public_key", "") or ""
        secret_key = getattr(settings, "langfuse_secret_key", "") or ""

    if public_key and secret_key:
        return _LangfuseEmitter(public_key, secret_key, settings)

    return _LocalEmitter()


class _LangfuseEmitter:
    """Langfuse-backed emitter with safe degradation."""

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        settings: Any,
    ) -> None:
        self._public_key = public_key
        self._secret_key = secret_key
        self._base_url = getattr(settings, "langfuse_base_url", "") or ""
        # Lazy import — only when the factory decides to use Langfuse.
        self._client: Any | None = None
        self._client_ready: bool = False
        try:
            from langfuse import Langfuse  # noqa: F811

            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=self._base_url,
            )
            self._client_ready = True
        except Exception:
            self._client_ready = False

    def start_trace(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> TraceContext:
        if self._client_ready:
            try:
                trace = self._client.trace(name=name, metadata=metadata or {})
                return TraceContext(
                    trace_id=str(trace.id),
                    name=name,
                    metadata=metadata or {},
                )
            except Exception:
                pass
        return start_local_trace(name, metadata)

    def event(
        self,
        trace_id: str,
        event_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if self._client_ready:
            try:
                self._client.event(
                    trace_id=trace_id,
                    name=event_name,
                    input=metadata or {},
                )
            except Exception:
                pass

    def score(
        self,
        trace_id: str,
        name: str,
        value: float | int | str | bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if self._client_ready:
            try:
                self._client.score(
                    trace_id=trace_id,
                    name=name,
                    value=float(value) if isinstance(value, (int, float)) else 1.0,
                    metadata=metadata or {},
                )
            except Exception:
                pass
