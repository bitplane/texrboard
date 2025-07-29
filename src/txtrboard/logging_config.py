"""Logging configuration for TextBoard application.

This module sets up structured logging to help debug issues and monitor
the application's behavior during development and production use.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "DEBUG", log_file: Optional[str] = None, console: bool = True) -> None:
    """Configure logging for the TextBoard application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to ./logs/textboard.log)
        console: Whether to also log to console
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Default log file
    if log_file is None:
        log_file = logs_dir / "textboard.log"
    else:
        log_file = Path(log_file)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (if enabled)
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Less verbose on console
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Log the setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {level}, File: {log_file}")

    # Reduce noise from some third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
