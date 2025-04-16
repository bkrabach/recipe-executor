import argparse
import asyncio
import os
import sys
from typing import Dict, List

import debugpy
from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_context_args(args: List[str]) -> Dict[str, str]:
    """Parse command line arguments into context key-value pairs."""
    context_dict = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            context_dict[key] = value
        else:
            # If no equals sign, treat the whole thing as a key with empty value
            context_dict[arg] = ""
    return context_dict


async def execute_recipe(recipe_path: str, context_args: List[str], log_dir: str) -> None:
    """Execute a recipe using recipe_executor."""
    # Initialize logger
    logger = init_logger(log_dir=log_dir)
    logger.info(f"Executing recipe: {recipe_path}")

    # Parse context arguments
    context_dict = parse_context_args(context_args)
    logger.debug(f"Context arguments: {context_dict}")

    # Create context and executor
    context = Context(artifacts=context_dict)
    executor = Executor(logger)

    # Execute the recipe
    try:
        await executor.execute(recipe_path, context)
        logger.info("Recipe execution completed successfully")
    except Exception as e:
        logger.error(f"Recipe execution failed: {e}")
        raise


async def create_recipe(idea_path: str, context_args: List[str], log_dir: str) -> None:
    """Create a recipe from an idea file using recipe_creator."""
    # Initialize logger
    logger = init_logger(log_dir=log_dir)
    logger.info(f"Creating recipe from idea: {idea_path}")

    # Parse context arguments
    context_dict = parse_context_args(context_args)

    # Files parameter handling - passed as-is to the recipe creator
    if "files" in context_dict:
        logger.debug(f"Files parameter: {context_dict['files']}")

    # Add the idea path as the input context variable
    context_dict["input"] = idea_path
    logger.debug(f"Context arguments: {context_dict}")

    # Create context and executor
    context = Context(artifacts=context_dict)
    executor = Executor(logger)

    # Path to the recipe creator recipe
    creator_recipe_path = "recipes/recipe_creator/create.json"

    # Make sure the recipe creator recipe exists
    if not os.path.exists(creator_recipe_path):
        logger.error(f"Recipe creator recipe not found: {creator_recipe_path}")
        raise FileNotFoundError(f"Recipe creator recipe not found: {creator_recipe_path}")

    # Execute the recipe creator
    try:
        await executor.execute(creator_recipe_path, context)
        logger.info("Recipe creation completed successfully")
    except Exception as e:
        logger.error(f"Recipe creation failed: {e}")
        raise


async def main_async() -> None:
    """Async entry point for the recipe tool."""
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(description="Recipe Tool - Unified interface for recipe execution and creation")

    # Create command group
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument("--execute", metavar="RECIPE_PATH", help="Execute a recipe JSON file")
    command_group.add_argument("--create", metavar="IDEA_PATH", help="Create a recipe from an idea file")

    # Add log directory option
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")

    # Add debug option
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    # Capture remaining arguments to use as context variables
    args, remaining = parser.parse_known_args()

    # Enable debugpy if debug mode is on
    if args.debug:
        debugpy.listen(("localhost", 5678))
        print("Debugging enabled. Attach your debugger to localhost:5678.")
        debugpy.wait_for_client()

    # Determine which command to run
    if args.execute:
        await execute_recipe(args.execute, remaining, args.log_dir)
    elif args.create:
        await create_recipe(args.create, remaining, args.log_dir)


def main() -> None:
    """Entry point for the recipe tool."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.stderr.write("Execution interrupted by user.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
