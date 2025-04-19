import logging
import os
from typing import Optional

def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes and configures a logger instance writing to stdout and separate log files per level.
    Clears existing log files on each run.

    Args:
        log_dir (str): Directory for log files. Default: "logs".
        stdio_log_level (str): Log level for stdout. Default: "INFO". Case-insensitive.
            Options: "DEBUG", "INFO", "WARN", "ERROR".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If logger setup or file/directory access fails.
    """
    logger_name: str = "recipe_executor"
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Remove all previous handlers for full reset
    while logger.handlers:
        logger.handlers.pop()

    formatter: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Ensure log directory exists
    try:
        if not os.path.isdir(log_dir):
            logger.debug(f"Log directory '{log_dir}' does not exist. Attempting to create it.")
            os.makedirs(log_dir, exist_ok=True)
            logger.debug(f"Log directory '{log_dir}' created.")
    except Exception as error:
        error_message: str = f"Failed to create log directory '{log_dir}': {error}"
        logger.error(error_message)
        raise Exception(error_message)

    # Set up file handlers for debug, info, and error
    log_file_defs = [
        ("debug", os.path.join(log_dir, "debug.log"), logging.DEBUG),
        ("info", os.path.join(log_dir, "info.log"), logging.INFO),
        ("error", os.path.join(log_dir, "error.log"), logging.ERROR)
    ]

    for log_name, log_path, level in log_file_defs:
        try:
            file_handler: logging.FileHandler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.debug(f"Added file handler for '{log_path}' at level '{logging.getLevelName(level)}'.")
        except Exception as error:
            error_message: str = f"Failed to open log file '{log_path}': {error}"
            logger.error(error_message)
            raise Exception(error_message)

    # Set up stdout handler at INFO level by default
    try:
        stdio_log_level_norm: str = stdio_log_level.strip().upper()
        stdio_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARNING,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        stdio_level: int = stdio_map.get(stdio_log_level_norm, logging.INFO)
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(stdio_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.debug(f"Added stdout handler at level '{stdio_log_level_norm}'.")
    except Exception as error:
        error_message: str = f"Failed to initialize stdout logging: {error}"
        logger.error(error_message)
        raise Exception(error_message)

    logger.info("Logger initialized successfully.")
    return logger
