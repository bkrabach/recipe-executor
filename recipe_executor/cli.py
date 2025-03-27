#!/usr/bin/env python3
import argparse
import logging
import sys

from recipe_executor.logger_setup import setup_logging
from recipe_executor.preprocessor import parse_recipe
from recipe_executor.executor import execute_recipe

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute a recipe from a Markdown file."
    )
    parser.add_argument(
        "recipe_path",
        help="Path to the recipe Markdown file"
    )
    parser.add_argument(
        "--root",
        help="Root directory for file operations",
        default=None
    )
    parser.add_argument(
        "--console-level",
        help="Console log level (e.g., DEBUG, INFO, WARNING, ERROR)",
        default=None
    )
    args = parser.parse_args()

    # Determine the effective root directory: CLI arg overrides config.
    from recipe_executor.config import ROOT_DIR as config_root
    effective_root = args.root or config_root

    # Include the effective root in the execution context.
    context = {"root": effective_root}

    # Set up logging, passing console level from CLI (or will use config's default if not provided).
    setup_logging(console_level=args.console_level)

    logging.info("Using root directory: %s", effective_root)
    logging.info("Starting recipe execution for: %s", args.recipe_path)
    try:
        recipe = parse_recipe(args.recipe_path)
    except Exception as e:
        logging.error("Failed to parse recipe: %s", e)
        sys.exit(1)

    try:
        execute_recipe(recipe, context)
    except Exception as e:
        logging.error("Error during recipe execution: %s", e)
        sys.exit(1)

    logging.info("Recipe executed successfully.")

if __name__ == "__main__":
    main()
