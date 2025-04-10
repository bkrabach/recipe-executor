import argparse
import sys
import time

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_context(context_list: list[str]) -> dict[str, str]:
    """
    Parses a list of context items in key=value format into a dictionary.

    Args:
        context_list (list[str]): List of context strings in key=value format.

    Returns:
        dict[str, str]: Parsed context dictionary.

    Raises:
        ValueError: If any context string is not in the key=value format.
    """
    context_data: dict[str, str] = {}
    for item in context_list:
        if "=" not in item:
            raise ValueError(f"Invalid context format '{item}'")
        key, value = item.split("=", 1)
        context_data[key] = value
    return context_data


def main() -> None:
    # Load environment variables from .env file if available
    load_dotenv()

    parser = argparse.ArgumentParser(description="Recipe Executor")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory to store log files")
    parser.add_argument("--context", action="append", default=[], help="Context values in key=value format")
    args = parser.parse_args()

    try:
        context_artifacts = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    try:
        logger = init_logger(args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {str(e)}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    logger.debug(f"Parsed arguments: {args}")
    logger.debug(f"Initial context artifacts: {context_artifacts}")

    # Create Context and Executor instances
    context = Context(artifacts=context_artifacts)
    executor = Executor()

    start_time = time.time()

    try:
        logger.info(f"Executing recipe: {args.recipe_path}")
        executor.execute(args.recipe_path, context, logger=logger)
        duration = time.time() - start_time
        logger.info(f"Recipe executed successfully in {duration:.2f} seconds.")
        sys.exit(0)
    except Exception as e:
        logger.error("An error occurred during recipe execution:", exc_info=True)
        sys.stderr.write(f"Recipe execution failed: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
