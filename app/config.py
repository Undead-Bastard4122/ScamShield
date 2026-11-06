"""Configuration loading and validation.

Secrets come from environment variables only. Error messages name the
variable but never include its value, and secret fields are excluded from
``repr`` so a ``Settings`` object is safe to log by accident.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from app.scanner.validator import DEFAULT_MAX_LENGTH

_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


class ConfigError(ValueError):
    """Raised for missing or invalid configuration. Never contains values."""


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str | None = field(default=None, repr=False)
    log_level: str = "INFO"
    max_input_length: int = DEFAULT_MAX_LENGTH


def load_settings(
    env: Mapping[str, str] | None = None,
    *,
    require_bot_token: bool = False,
) -> Settings:
    """Load settings from ``env`` (default: the process environment).

    The bot token is optional by default so the input engine and tests run
    without secrets; pass ``require_bot_token=True`` when starting the bot.
    """
    source = os.environ if env is None else env

    token = (source.get("TELEGRAM_BOT_TOKEN") or "").strip() or None
    if require_bot_token and token is None:
        raise ConfigError("TELEGRAM_BOT_TOKEN is required but not set.")

    log_level = (source.get("LOG_LEVEL") or "INFO").strip().upper()
    if log_level not in _LOG_LEVELS:
        raise ConfigError("LOG_LEVEL is not a valid log level.")

    raw_length = (source.get("MAX_INPUT_LENGTH") or "").strip()
    max_length = DEFAULT_MAX_LENGTH
    if raw_length:
        if not (raw_length.isascii() and raw_length.isdigit()):
            raise ConfigError("MAX_INPUT_LENGTH must be a positive integer.")
        max_length = int(raw_length)
        if not 1 <= max_length <= DEFAULT_MAX_LENGTH:
            raise ConfigError(
                f"MAX_INPUT_LENGTH must be between 1 and {DEFAULT_MAX_LENGTH}."
            )

    return Settings(
        telegram_bot_token=token,
        log_level=log_level,
        max_input_length=max_length,
    )
