# recipe_executor/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if present

class Config:
    """
    Configuration settings for the Recipe Executor Tool.
    Values are loaded from environment variables or defaults.
    """
    # Directory containing recipe files
    RECIPES_DIR: str = os.getenv("RECIPES_DIR", "./recipes")
    # Root directory for outputs (e.g., file outputs)
    OUTPUT_ROOT: str = os.getenv("OUTPUT_ROOT", ".")
    # Directory for logs
    LOGS_DIR: str = os.getenv("LOGS_DIR", os.path.join(OUTPUT_ROOT, "logs"))
    # Default LLM model name for Pydantic-AI
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai:gpt-4.5")
    # Optionally, an API key for OpenAI (if needed by Pydantic-AI)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    @classmethod
    def ensure_directories(cls):
        """Ensure that important directories (recipes, output root, logs) exist."""
        if not os.path.isdir(cls.RECIPES_DIR):
            os.makedirs(cls.RECIPES_DIR, exist_ok=True)
        if not os.path.isdir(cls.OUTPUT_ROOT):
            os.makedirs(cls.OUTPUT_ROOT, exist_ok=True)
        if not os.path.isdir(cls.LOGS_DIR):
            os.makedirs(cls.LOGS_DIR, exist_ok=True)
