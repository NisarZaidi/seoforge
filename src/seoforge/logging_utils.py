"""Structured logging setup for SeoForge library use."""

from __future__ import annotations

import logging
from typing import Optional


def setup_logging(level: str = "INFO", *, quiet: bool = False) -> logging.Logger:
    logger = logging.getLogger("seoforge")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S")
    )
    logger.addHandler(handler)
    if quiet:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "seoforge")
