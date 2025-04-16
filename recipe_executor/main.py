import argparse
import asyncio
import sys
import time
import traceback
from typing import Dict, List

from dotenv import load_dotenv


def parse_context(context_args: List[str]) -> Dict[str, str]:
    """Parse --context key=value pairs into a dictionary of strings."""
    context_dict: Dict[str, str] = {}
    for item in context_args:
        if "=" not in item:
            raise ValueError(f"Invalid context format '{item}'; should be key=value")
        key, value = item.split("=", 1)
        context_dict[key] = value
    return context_dict


async def main_async() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Recipe Executor: Run automation recipes via CLI")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file to execute")
    parser.add_argument(
        "--log-dir", dest="log_dir", type=str, default="logs", help="Directory for log files (default: 'logs')"
    )
    parser.add_argument(
        "--context",
        dest="context",
        action="append",
        default=[],
        help="Context value as key=value pair (may specify multiple times)",
    )

    args = parser.parse_args()

    # Import logger, context, executor within function to avoid circular imports
    try:
        from recipe_executor.context import Context
        from recipe_executor.executor import Executor
        from recipe_executor.logger import init_logger
    except ImportError as exc:
        sys.stderr.write(f"Import error: {exc}\n")
        sys.exit(1)

    try:
        logger = init_logger(args.log_dir)
    except Exception as exc:
        sys.stderr.write(f"Logger Error: {exc}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    logger.debug(f"Parsed arguments: {args}")

    try:
        context_artifacts = parse_context(args.context)
    except ValueError as exc:
        sys.stderr.write(f"Context Error: {exc}\n")
        logger.error(f"Context Error: {exc}")
        sys.exit(1)

    logger.debug(f"Initial context artifacts: {context_artifacts}")
    context = Context(artifacts=context_artifacts)

    executor = Executor(logger)
    start_time = time.time()
    logger.info(f"Executing recipe: {args.recipe_path}")
    try:
        await executor.execute(args.recipe_path, context)
        elapsed = time.time() - start_time
        logger.info(f"Recipe execution succeeded in {elapsed:.2f} seconds.")
        print(f"Recipe execution succeeded in {elapsed:.2f} seconds.")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"An error occurred during recipe execution: {exc}")
        logger.error(traceback.format_exc())
        sys.stderr.write(f"Execution Error: {exc}\n{traceback.format_exc()}\n")
        sys.exit(1)


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.stderr.write("Interrupted by user.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
