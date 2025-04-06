"""
Utility functions for the Blueprint CLI tool.

This module provides common utility functions used throughout the tool.
"""

import logging
import os
import sys
import threading
from typing import Dict, List, Optional

# Global print lock to prevent output interleaving
print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """
    Thread-safe print function to prevent output interleaving.

    Args:
        *args: Arguments to pass to the print function
        **kwargs: Keyword arguments to pass to the print function
    """
    with print_lock:
        print(*args, **kwargs)


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(level=level, format=log_format, handlers=[logging.StreamHandler(sys.stdout)])

    # Add file handler if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)


def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path

    Returns:
        Absolute path to the directory

    Raises:
        OSError: If directory creation fails
    """
    os.makedirs(directory, exist_ok=True)
    return os.path.abspath(directory)


def format_files_for_recipe(files: List[Dict[str, str]]) -> str:
    """
    Format a list of file dictionaries for use in a recipe.

    Args:
        files: List of {path: rationale} dictionaries

    Returns:
        Comma-separated list of file paths
    """
    return ",".join(item["path"] for item in files)


def load_file_content(file_path: str) -> str:
    """
    Load the content of a file.

    Args:
        file_path: Path to the file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file_content(file_path: str, content: str) -> None:
    """
    Write content to a file, creating directories if necessary.

    Args:
        file_path: Path to the file
        content: Content to write

    Raises:
        IOError: If file cannot be written
    """
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory(directory)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
