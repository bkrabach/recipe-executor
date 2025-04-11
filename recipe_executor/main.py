import argparse
import asyncio
import sys
import time
import traceback

from dotenv import load_dotenv

from recipe_executor.logger import init_logger
from recipe_executor.context import Context
from recipe_executor.executor import Executor


def parse_context(context_args: list[str]) -> dict[str, str]:
    """Parse a list of context key=value strings into a dictionary."""
    context_data: dict[str, str] = {}
    for item in context_args:
        if '=' not in item:
            raise ValueError(f"Invalid context format: '{item}'. Expected format is key=value.")
        key, value = item.split('=', 1)
        context_data[key] = value
    return context_data


async def main_async() -> None:
    # Load environment variables from .env file
    load_dotenv()

    # Setup argument parsing
    parser = argparse.ArgumentParser(description="Recipe Executor Tool")
    parser.add_argument("recipe_path", help="Path to the recipe file to execute")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Context key=value pairs. Can be repeated.")

    args = parser.parse_args()

    # Parse context values
    try:
        context_data = parse_context(args.context)
    except ValueError as ve:
        sys.stderr.write(f"Context Error: {ve}\n")
        sys.exit(1)

    # Initialize logger
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger initialization failed: {e}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    logger.debug(f"Parsed arguments: {args}")
    logger.debug(f"Initial context data: {context_data}")

    # Create Context and Executor instances
    context = Context(artifacts=context_data)  
    executor = Executor()

    start_time = time.time()
    try:
        logger.info(f"Executing recipe: {args.recipe_path}")
        # Await the execution of the recipe
        await executor.execute(args.recipe_path, context, logger=logger)
        elapsed = time.time() - start_time
        logger.info(f"Recipe executed successfully in {elapsed:.2f} seconds")
    except Exception as e:
        error_message = f"An error occurred during recipe execution: {e}"
        logger.error(error_message, exc_info=True)
        sys.stderr.write(f"{error_message}\n{traceback.format_exc()}\n")
        sys.exit(1)


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.stderr.write("Execution interrupted by user.\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
