import logging
import logging.handlers
import os
from typing import Optional


def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR".
            Note: This is not case-sensitive.
            If set to "DEBUG", all logs will be printed to stdout.
            If set to "INFO", only INFO and higher level logs will be printed to stdout.

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    logger_name: str = "recipe_executor"
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Remove all handlers from the logger (reset)
    while logger.handlers:
        logger.handlers.pop()

    # Custom log formatter
    formatter: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Prepare log directory
    try:
        if not os.path.isdir(log_dir):
            logger.debug(f"Log directory '{log_dir}' does not exist. Attempting to create it.")
            os.makedirs(log_dir, exist_ok=True)
            logger.debug(f"Log directory '{log_dir}' created.")
    except Exception as e:
        error_message = f"Failed to create log directory '{log_dir}': {e}"
        logger.error(error_message)
        raise Exception(error_message)

    # Log file definitions
    log_files = {
        'debug': (os.path.join(log_dir, 'debug.log'), logging.DEBUG),
        'info': (os.path.join(log_dir, 'info.log'), logging.INFO),
        'error': (os.path.join(log_dir, 'error.log'), logging.ERROR),
    }
    file_handlers = []
    for name, (file_path, log_level) in log_files.items():
        try:
            file_handler: logging.FileHandler = logging.FileHandler(file_path, mode='w', encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            file_handlers.append(file_handler)
            logger.addHandler(file_handler)
            logger.debug(f"Added file handler for '{file_path}' at level '{logging.getLevelName(log_level)}'.")
        except Exception as e:
            error_message = f"Failed to create/open log file '{file_path}': {e}"
            logger.error(error_message)
            raise Exception(error_message)

    # Stdout handler (console)
    try:
        stdio_log_level_norm: str = stdio_log_level.strip().upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARNING,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
        }
        stdio_level: int = level_map.get(stdio_log_level_norm, logging.INFO)
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(stdio_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.debug(f"Added stdout handler at level '{stdio_log_level_norm}'.")
    except Exception as e:
        error_message = f"Failed to initialize stdout logging: {e}"
        logger.error(error_message)
        raise Exception(error_message)

    logger.info("Logger initialized successfully.")
    return logger
