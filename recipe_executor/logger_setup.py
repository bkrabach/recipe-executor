"""
Logging Setup Module for the Recipe Executor CLI tool.

This module configures three log files:
  - debug.log: Captures all messages at DEBUG level and above.
  - info.log: Captures messages at INFO level and above.
  - error.log: Captures messages at ERROR level and above.

Each run starts with fresh logs (the files are overwritten).
A console handler is also added for warnings and above.
"""

import logging
import os

from .config import CONSOLE_LOG_LEVEL, LOGS_DIR

def setup_logging(console_level: str | None = None) -> None:
    # Create the log directory if it doesn't exist.
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Get the root logger and clear existing handlers.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    # Remove any existing handlers.
    while root_logger.handlers:
        root_logger.handlers.pop()

    # Define a common formatter.
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Debug log handler.
    debug_handler = logging.FileHandler(os.path.join(LOGS_DIR, "debug.log"), mode="w")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    root_logger.addHandler(debug_handler)

    # Info log handler.
    info_handler = logging.FileHandler(os.path.join(LOGS_DIR, "info.log"), mode="w")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    root_logger.addHandler(info_handler)

    # Error log handler.
    error_handler = logging.FileHandler(os.path.join(LOGS_DIR, "error.log"), mode="w")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Console log handler.
    # Use the provided console_level or fall back to the config value.
    if console_level is None:
        console_level = CONSOLE_LOG_LEVEL
    # Convert string level to numeric level.
    numeric_level = getattr(logging, console_level.upper(), logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root_logger.addHandler(console_handler)
