# recipe_executor/cli.py

import argparse
import sys
import os
from recipe_executor import config, parser, executor

def main():
    # Set up argument parser for CLI options
    arg_parser = argparse.ArgumentParser(prog="recipe_executor", description="Run a specified recipe file.")
    arg_parser.add_argument("--recipe", "-r", required=True,
                            help="Name or path of the recipe to execute")
    arg_parser.add_argument("--recipes-dir",
                            help="Directory containing recipes (overrides RECIPES_DIR from .env)")
    arg_parser.add_argument("--root",
                            help="Output root directory for file outputs (overrides OUTPUT_ROOT from .env)")
    args = arg_parser.parse_args()

    # Override configuration with CLI arguments if provided
    if args.recipes_dir:
        config.Config.RECIPES_DIR = args.recipes_dir
    if args.root:
        config.Config.OUTPUT_ROOT = args.root
        # If LOGS_DIR not explicitly set in environment, use the new root for logs
        if not os.getenv("LOGS_DIR"):
            config.Config.LOGS_DIR = os.path.join(config.Config.OUTPUT_ROOT, "logs")
    # Ensure required directories exist (recipes, output, logs)
    config.Config.ensure_directories()
    # Initialize logging
    executor.setup_logging()

    # Parse the specified recipe file
    try:
        recipe = parser.parse_recipe(args.recipe)
    except Exception as e:
        print(f"Failed to load recipe: {e}", file=sys.stderr)
        sys.exit(1)
    # Execute the recipe
    try:
        executor.execute_recipe(recipe)
    except Exception as e:
        print(f"Recipe execution failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
