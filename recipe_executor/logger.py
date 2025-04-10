import logging
import os
import sys
from logging import Logger
from typing import Optional


def init_logger(log_dir: str = "logs") -> Logger:
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
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Reset any existing handlers to ensure consistent configuration
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create log directory if it does not exist, with error handling
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        # Log to stderr since file logging isn't configured yet
        error_message = f"Failed to create log directory '{log_dir}': {e}"
        sys.stderr.write(error_message + "\n")
        raise Exception(error_message)

    # Define a consistent log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Create File Handlers with mode 'w' to clear previous logs
    try:
        debug_file = os.path.join(log_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_file, mode='w')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        info_file = os.path.join(log_dir, "info.log")
        info_handler = logging.FileHandler(info_file, mode='w')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        error_file = os.path.join(log_dir, "error.log")
        error_handler = logging.FileHandler(error_file, mode='w')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
    except Exception as e:
        error_message = f"Failed to set up log file handlers: {e}"
        sys.stderr.write(error_message + "\n")
        raise Exception(error_message)

    # Create console (stdout) handler with level INFO
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add all handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    # Log debug message for initialization
    logger.debug("Initializing logger component")

    return logger
