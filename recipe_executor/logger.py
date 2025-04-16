import logging
import os
from logging import Logger
from typing import Dict


def init_logger(log_dir: str = "logs", stdio_log_level: str = "INFO") -> Logger:
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
    # --- Logger settings ---
    logger_name: str = "recipe_executor"
    log_levels: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_file_configs = [
        ("debug.log", logging.DEBUG),
        ("info.log", logging.INFO),
        ("error.log", logging.ERROR),
    ]
    log_format: str = "%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s"
    log_datefmt: str = "%Y-%m-%d %H:%M:%S"

    # --- Level detection (for stdio/console handler) ---
    stdio_log_level_upper: str = stdio_log_level.strip().upper()
    if stdio_log_level_upper not in log_levels:
        raise ValueError(f"Invalid stdio_log_level: {stdio_log_level}. Options are: {', '.join(log_levels.keys())}")
    console_log_level: int = log_levels[stdio_log_level_upper]

    # --- Construct log dir ---
    try:
        if not os.path.exists(log_dir):
            # DEBUG: log directory creation
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"Logger: Creating log directory at '{log_dir}'")
            os.makedirs(log_dir, exist_ok=True)
    except Exception as create_dir_exc:
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Logger: Failed to create log directory '{log_dir}': {create_dir_exc}")
        raise Exception(f"Logger: Failed to create log directory '{log_dir}': {create_dir_exc}") from create_dir_exc

    # --- Obtain or create logger ---
    logger: Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # --- Remove all existing handlers ---
    while logger.handlers:
        handler = logger.handlers[0]
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(fmt=log_format, datefmt=log_datefmt)
    handlers = []

    # --- Console handler (stdout) ---
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    except Exception as exc:
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Logger: Failed to create stdout handler: {exc}")
        raise Exception("Logger: Failed to create stdout handler.") from exc

    # --- Per-level file handlers ---
    for file_name, level in log_file_configs:
        file_path = os.path.join(log_dir, file_name)
        try:
            file_handler = logging.FileHandler(file_path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as file_exc:
            logging.basicConfig(level=logging.ERROR)
            logging.error(f"Logger: Failed to set up '{file_name}': {file_exc}")
            raise Exception(f"Logger: Failed to set up '{file_name}': {file_exc}") from file_exc

    for handler in handlers:
        logger.addHandler(handler)

    # --- Debug log: logger initialized ---
    logger.debug(f"Logger initialized with dir '{log_dir}', stdio_log_level='{stdio_log_level_upper}'")
    logger.info("Logger initialized successfully")
    return logger
