import argparse
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from executor import RecipeExecutor

from recipe_executor.context import Context
from recipe_executor.logger import init_logger


def parse_args() -> Dict[str, Any]:
    """
    Parse command line arguments into a structured dictionary.
    
    Returns:
        Dict[str, Any]: Dictionary containing parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Executes a recipe with additional context information."
    )
    parser.add_argument("recipe_path", help="Path to the recipe file to execute")
    parser.add_argument("description", nargs="?", default=None, help="Product description (optional)")
    
    # Directories
    parser.add_argument("-i", "--input", dest="input_dir", help="Input directory for analysis")
    parser.add_argument("-o", "--output", dest="output_dir", help="Output directory for generated code")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    
    # Advanced options
    parser.add_argument("-c", "--context", action="append", default=[], 
                       help="Additional context values as key=value pairs")
    
    return vars(parser.parse_args())


def process_context_args(context_args: List[str]) -> Dict[str, str]:
    """
    Process context key=value pairs from command line arguments.
    
    Args:
        context_args: List of context arguments as key=value strings
        
    Returns:
        Dict[str, str]: Dictionary of processed context values
        
    Raises:
        ValueError: If any argument doesn't follow key=value format
    """
    context: Dict[str, str] = {}
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

    # Parse command line arguments
    args = parse_args()
    
    # Build context dictionary from all sources
    cli_context: Dict[str, Any] = {}
    
    # Parse context key=value pairs
    try:
        if args["context"]:
            cli_context.update(process_context_args(args["context"]))
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)
    
    # Add description if provided
    if args["description"]:
        cli_context["product_description"] = args["description"]
        
    # Add directory paths
    if args["input_dir"]:
        # First expand any user path with tilde (~)
        input_dir = os.path.expanduser(args["input_dir"])
        
        # If it's an absolute path, use it directly
        # Otherwise, make it absolute relative to current directory
        if not os.path.isabs(input_dir):
            input_dir = os.path.abspath(input_dir)
            
        cli_context["input_dir"] = input_dir
        
    if args["output_dir"]:
        # Handle output directory path correctly
        # First expand any user path with tilde (~)
        output_dir = os.path.expanduser(args["output_dir"])
        
        # If it's an absolute path, use it directly
        # Otherwise, make it absolute relative to current directory
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)
        
        cli_context["output_dir"] = output_dir
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

    # Initialize logging
    logger = init_logger(args["log_dir"])
    logger.info("Starting Recipe Executor Tool")

    # Create the Context object with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        # Execute the recipe
        executor = RecipeExecutor()
        executor.execute(args["recipe_path"], context, logger=logger)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
