"""
Recipe executor module for the Blueprint CLI tool.

This module provides functions for executing recipes with the recipe_executor.
"""

import logging
import os
import subprocess
from typing import Dict

# Local imports
from utils import safe_print

logger = logging.getLogger(__name__)


def run_recipe(recipe_path: str, context: Dict[str, str], verbose: bool = False) -> bool:
    """
    Run a recipe with recipe_executor.

    Args:
        recipe_path: Path to the recipe file
        context: Context dictionary to pass to the recipe
        verbose: Whether to show verbose output

    Returns:
        True if the recipe executed successfully, False otherwise
    """
    # Find recipe_executor assuming we're running from parent directory
    # This allows flexibility in where blueprint_cli is located
    recipe_executor_path = "recipe_executor/main.py"

    # Verify path exists
    if not os.path.exists(recipe_executor_path):
        logger.warning(f"Recipe executor not found at {recipe_executor_path}. Trying relative path.")

        # Try a relative path from this script
        module_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(module_dir)
        alternate_path = os.path.join(parent_dir, "recipe_executor", "main.py")

        if os.path.exists(alternate_path):
            recipe_executor_path = alternate_path
        else:
            logger.error("Recipe executor not found. Make sure you're running from the parent directory.")
            return False

    # Construct command
    cmd = ["python", recipe_executor_path, recipe_path]

    # Add context parameters
    for key, value in context.items():
        cmd.extend(["--context", f"{key}={value}"])

    logger.debug(f"Running recipe: {' '.join(cmd)}")

    # Run command
    if verbose:
        # Show all output in real-time
        safe_print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        success = result.returncode == 0
    else:
        # Only show summary
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        if success:
            logger.info(f"Recipe completed successfully: {recipe_path}")
        else:
            logger.error(f"Error running recipe: {result.stderr}")

    return success


def get_recipe_path(recipe_name: str) -> str:
    """
    Get the full path to a recipe file.

    Args:
        recipe_name: Name of the recipe file

    Returns:
        Full path to the recipe file
    """
    # Get the directory of this module (works regardless of installation location)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    recipes_dir = os.path.join(module_dir, "recipes")

    # Ensure recipes directory exists
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir, exist_ok=True)

    return os.path.join(recipes_dir, recipe_name)
