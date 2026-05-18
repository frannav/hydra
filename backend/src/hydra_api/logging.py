"""HYDRA API — Safe logging configuration.

Ensures that sensitive values (API keys, headers, secrets)
are never printed to logs.
"""

import logging
from typing import Any


def _mask_sensitive(value: str) -> str:
    """Mask a sensitive string, showing only first and last 4 chars."""
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]


class _SensitiveFormatter(logging.Formatter):
    """Formatter that masks log values based on key names.

    If a logging key contains a sensitive keyword (api_key, secret, token,
    password, authorization, key), the corresponding value is masked.
    """

    _SENSITIVE_KEY_PATTERNS = (
        "api_key",
        "secret",
        "token",
        "password",
        "authorization",
        "key",
    )

    def _is_sensitive_key(self, key: str) -> bool:
        """Return True if *key* looks like a sensitive field name."""
        lower = key.lower()
        return any(pat in lower for pat in self._SENSITIVE_KEY_PATTERNS)

    def _mask_value(self, key: str, value: Any) -> Any:
        """Mask *value* when *key* is identified as sensitive."""
        if self._is_sensitive_key(key) and isinstance(value, str):
            return _mask_sensitive(value)
        return value

    def format(self, record: logging.LogRecord) -> str:
        # Mask dict-style logging args so the formatted message never
        # leaks secrets.
        if hasattr(record, "args") and isinstance(record.args, dict):
            masked = {k: self._mask_value(k, v) for k, v in record.args.items()}
            record.args = masked
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with safe formatting.

    Idempotent: does not add duplicate handlers on repeated calls.
    Updates every existing StreamHandler to use _SensitiveFormatter
    so that secrets are never leaked, even when multiple handlers
    are present.
    """
    safe_handler = logging.StreamHandler()
    safe_handler.setFormatter(
        _SensitiveFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Update any existing StreamHandler to use _SensitiveFormatter.
    # Iterate over a copy to avoid mutating the list during iteration.
    for h in list(root.handlers):
        if isinstance(h, logging.StreamHandler):
            if not isinstance(h.formatter, _SensitiveFormatter):
                h.setFormatter(
                    _SensitiveFormatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                )

    # Only add if we still have no handler.
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(safe_handler)
