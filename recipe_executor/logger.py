import logging
import os
import sys
from typing import Optional


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Create log directory if it doesn’t exist
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        error_message = f"Failed to create log directory '{log_dir}': {e}"
        print(error_message, file=sys.stderr)
        raise Exception(error_message) from e

    # Create or get the logger for RecipeExecutor
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all messages
    logger.propagate = False  # Avoid duplicate logs if root logger is configured

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define log format
    log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # File handler for DEBUG level (all messages)
    try:
        debug_handler = logging.FileHandler(os.path.join(log_dir, "debug.log"), mode='w')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(log_format)
        logger.addHandler(debug_handler)
    except Exception as e:
        error_message = f"Failed to create debug log file: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

    # File handler for INFO level and above
    try:
        info_handler = logging.FileHandler(os.path.join(log_dir, "info.log"), mode='w')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(log_format)
        logger.addHandler(info_handler)
    except Exception as e:
        error_message = f"Failed to create info log file: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

    # File handler for ERROR level and above
    try:
        error_handler = logging.FileHandler(os.path.join(log_dir, "error.log"), mode='w')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(log_format)
        logger.addHandler(error_handler)
    except Exception as e:
        error_message = f"Failed to create error log file: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

    # Console handler for INFO level and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Log debug message indicating initialization
    logger.debug("Initializing RecipeExecutor logger with log directory: '%s'", log_dir)

    return logger
