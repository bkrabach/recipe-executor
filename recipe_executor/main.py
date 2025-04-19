import argparse
import asyncio
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_key_value_pairs(pairs: List[str], arg_name: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid {arg_name} format '{pair}'. Expected format: key=value.")
        key, value = pair.split("=", 1)
        if not key:
            raise ValueError(f"Invalid {arg_name} format '{pair}'. Key cannot be empty.")
        result[key] = value
    return result


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.stderr.write("\nExecution interrupted by user.\n")
        sys.exit(1)


async def main_async() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Recipe Executor: command-line recipe runner.")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory to write log files (default: 'logs').")
    parser.add_argument(
        "--context", action="append", default=[], help="Context artifact as key=value (can be repeated)."
    )
    parser.add_argument(
        "--config", action="append", default=[], help="Configuration value as key=value (can be repeated)."
    )
    args = parser.parse_args()

    logger: Optional[Any] = None
    exit_code: int = 0
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as exc:
        sys.stderr.write(f"Logger initialization failed: {str(exc)}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    start_time: float = time.time()

    try:
        logger.debug(f"Parsed arguments: {args}")
        try:
            artifacts: Dict[str, str] = parse_key_value_pairs(args.context, "--context")
            config: Dict[str, str] = parse_key_value_pairs(args.config, "--config")
        except ValueError as value_error:
            logger.error(f"Context Error: {str(value_error)}")
            sys.stderr.write(f"Context Error: {str(value_error)}\n")
            sys.exit(1)

        logger.debug(f"Initial context artifacts: {artifacts}")
        logger.debug(f"Initial config: {config}")

        context: Context = Context(artifacts=artifacts, config=config)
        executor: Executor = Executor(logger)

        logger.info(f"Executing recipe: {args.recipe_path}")
        await executor.execute(args.recipe_path, context)

        elapsed: float = time.time() - start_time
        logger.info(f"Recipe executed successfully in {elapsed:.2f} seconds.")
        print(f"Success: Recipe executed in {elapsed:.2f} seconds.")
        exit_code = 0
    except Exception as exc:
        if logger is not None:
            logger.error(f"An error occurred during recipe execution: {str(exc)}")
            logger.error(traceback.format_exc())
        sys.stderr.write(f"Execution failed: {str(exc)}\n")
        sys.stderr.write(traceback.format_exc())
        exit_code = 1
    sys.exit(exit_code)
