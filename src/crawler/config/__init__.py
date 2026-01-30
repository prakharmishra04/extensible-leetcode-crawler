"""
Configuration package for the crawler application.

This package provides configuration management including:
- Structured logging with JSON formatting
- Settings management (to be implemented)
"""

from .logging_config import (
    setup_logging,
    get_logger,
    configure_default_logging,
    configure_production_logging,
    JSONFormatter,
    ConsoleFormatter,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
)

__all__ = [
    "setup_logging",
    "get_logger",
    "configure_default_logging",
    "configure_production_logging",
    "JSONFormatter",
    "ConsoleFormatter",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
