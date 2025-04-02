import os
import sys
import logging
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
    # Create log directory if it doesn't exist
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            # Log creation of directory if running in debug mode later
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Define log file paths
    debug_log = os.path.join(log_dir, "debug.log")
    info_log = os.path.join(log_dir, "info.log")
    error_log = os.path.join(log_dir, "error.log")

    # Common log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Get logger instance with a specific name
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Set logger to capture all messages

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    try:
        # Debug file handler: logs all messages
        debug_handler = logging.FileHandler(debug_log, mode="w")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)

        # Info file handler: logs INFO and above
        info_handler = logging.FileHandler(info_log, mode="w")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)

        # Error file handler: logs ERROR and above
        error_handler = logging.FileHandler(error_log, mode="w")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # Console handler: logs INFO and above to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    except Exception as e:
        raise Exception(f"Failed to set up logging handlers: {e}")

    # Log debug message indicating logger initialization
    logger.debug(f"Logger initialized. Log directory: {log_dir}")

    return logger
