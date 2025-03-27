"""
Configuration module for the Recipe Executor CLI tool.

This module loads environment variables (optionally from a .env file)
and sets up default configuration values for the application.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file if present.
load_dotenv()

def get_env(name: str, default: str | None = None) -> str:
    """
    Retrieve the value of an environment variable.

    Args:
        name: The name of the environment variable.
        default: A default value if the environment variable is not set.

    Returns:
        The environment variable's value or the default (or empty string).
    """
    value = os.getenv(name, default)
    if value is None:
        logging.warning("Environment variable '%s' is not set; defaulting to empty string", name)
        return ""
    return value

# Core configuration variables.
DEFAULT_MODEL = get_env("DEFAULT_MODEL", "openai:gpt-4.5")
PREPROCESSOR_MODEL = get_env("PREPROCESSOR_MODEL", DEFAULT_MODEL)
RECIPES_DIR = get_env("RECIPES_DIR", "./recipes")
OUTPUT_ROOT = get_env("OUTPUT_ROOT", "./outputs")
LOGS_DIR = get_env("LOGS_DIR", os.path.join(OUTPUT_ROOT, "logs"))
