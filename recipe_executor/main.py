import argparse
import sys
import time
import traceback
from typing import Dict, Optional

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_context(context_list: Optional[list]) -> Dict[str, str]:
    """
    Parse a list of key=value pairs into a dictionary.

    Args:
        context_list: List of strings in the format key=value.

    Returns:
        Dictionary with keys and values as strings.

    Raises:
        ValueError: If any of the context items is not in key=value format.
    """
    context_dict: Dict[str, str] = {}
    if not context_list:
        return context_dict

    for item in context_list:
        if "=" not in item:
            raise ValueError(f"Invalid context format: '{item}'. Expected key=value.")
        key, value = item.split("=", 1)
        if not key:
            raise ValueError(f"Context key cannot be empty in pair: '{item}'.")
        context_dict[key] = value
    return context_dict


def main() -> None:
    # Load environment variables as early as possible
    load_dotenv()

    # Setup argument parser
    parser = argparse.ArgumentParser(description="Recipe Executor Tool")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file to execute")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory for log files (default: logs)")
    parser.add_argument(
        "--context", action="append", help="Context values as key=value pairs (can be used multiple times)"
    )

    args = parser.parse_args()

    start_time = time.time()

    # Parse context values from command-line
    try:
        context_artifacts = parse_context(args.context)
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Initialize logger
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger initialization failed: {str(e)}\n")
        sys.exit(1)

    logger.debug(f"Starting main function with arguments: {args}")
    logger.debug(f"Context artifacts: {context_artifacts}")

    # Initialize Executor
    executor = Executor()

    # Create the execution context
    context = Context(executor=executor, artifacts=context_artifacts)

    try:
        logger.info("Starting Recipe Executor Tool")
        logger.info(f"Executing recipe: {args.recipe_path}")

        executor.execute(args.recipe_path, context, logger=logger)

        elapsed_time = time.time() - start_time
        logger.info(f"Recipe executed successfully in {elapsed_time:.2f} seconds")

    except Exception as e:
        error_message = f"An error occurred during recipe execution: {str(e)}"
        logger.error(error_message, exc_info=True)
        sys.stderr.write(error_message + "\n")
        sys.stderr.write(traceback.format_exc() + "\n")
        sys.exit(1)

    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
