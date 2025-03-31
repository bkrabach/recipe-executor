import argparse
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from executor import RecipeExecutor

from recipe_executor.context import Context
from recipe_executor.logger import init_logger


def parse_context(context_args: List[str]) -> Dict[str, Any]:
    """
    Parse context key=value pairs from the CLI arguments.

    Args:
        context_args: List of context arguments as key=value strings.

    Returns:
        A dictionary with key-value pairs parsed from the arguments.

    Raises:
        ValueError: If any argument does not follow key=value format.
    """
    context: Dict[str, Any] = {}
    for arg in context_args:
        if "=" not in arg:
            raise ValueError(f"Invalid context argument '{arg}'. Expected format: key=value")
        key, value = arg.split("=", 1)
        if not key:
            raise ValueError(f"Empty key in context argument '{arg}'.")
        context[key] = value
    return context


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    This function parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    It also handles errors and provides appropriate exit codes.
    """
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Executes a recipe with additional context information."
    )
    parser.add_argument("recipe_path", help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Additional context values as key=value pairs")
    parser.add_argument("--description", help="Product description for recipe generation")
    parser.add_argument("--input-dir", help="Input directory for analysis (defaults to current working directory)")
    parser.add_argument("--output-dir", help="Output directory for generated code (defaults to current working directory)")

    args = parser.parse_args()

    # Parse context key=value pairs
    try:
        cli_context = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Add the product description to the context if provided
    if args.description:
        cli_context["product_description"] = args.description

    # Add directory paths to the context if provided
    if args.input_dir:
        cli_context["input_dir"] = os.path.abspath(args.input_dir)
    
    if args.output_dir:
        cli_context["output_dir"] = os.path.abspath(args.output_dir)
        # Ensure the output directory exists
        os.makedirs(args.output_dir, exist_ok=True)

    # Initialize logging
    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Create the Context object with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        # Execute the recipe
        executor = RecipeExecutor()
        executor.execute(args.recipe_path, context, logger=logger)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
