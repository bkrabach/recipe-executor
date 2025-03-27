#!/usr/bin/env python3
import argparse
import logging
import sys

from recipe_executor.logger_setup import setup_logging
from recipe_executor.preprocessor import parse_recipe
from recipe_executor.executor import execute_recipe

def main() -> None:
    # Set up logging (this will overwrite previous log files on each run)
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Execute a recipe from a Markdown file."
    )
    parser.add_argument(
        "recipe_path",
        help="Path to the recipe Markdown file"
    )
    args = parser.parse_args()

    logging.info("Starting recipe execution for: %s", args.recipe_path)
    try:
        recipe = parse_recipe(args.recipe_path)
    except Exception as e:
        logging.error("Failed to parse recipe: %s", e)
        sys.exit(1)

    try:
        execute_recipe(recipe)
    except Exception as e:
        logging.error("Error during recipe execution: %s", e)
        sys.exit(1)

    logging.info("Recipe executed successfully.")

if __name__ == "__main__":
    main()
