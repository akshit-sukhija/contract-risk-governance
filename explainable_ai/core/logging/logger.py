"""Project-wide logger utility based on Python built-in logging."""

from __future__ import annotations

import logging
from threading import Lock


_CONFIG_LOCK = Lock()
_IS_CONFIGURED = False


def _configure_logging_once() -> None:
    global _IS_CONFIGURED

    if _IS_CONFIGURED:
        return

    with _CONFIG_LOCK:
        if _IS_CONFIGURED:
            return
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        _IS_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance for the provided name."""
    _configure_logging_once()
    return logging.getLogger(name)
