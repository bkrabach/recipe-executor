#!/usr/bin/env python3
"""
Command-line interface for the Blueprint CLI tool.

This module handles argument parsing and dispatches commands
to the appropriate modules.
"""

import argparse
import logging
import os
import sys
from typing import List, Optional

# Import local modules using relative paths based on script location
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Local imports
from analyzer import analyze_project  # noqa: E402
from config import create_config_from_args  # noqa: E402
from splitter import split_project_recursively  # noqa: E402
from utils import ensure_directory, setup_logging  # noqa: E402

# Get version from package or default if not available
try:
    from __init__ import __version__
except ImportError:
    __version__ = "0.1.0"


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Blueprint CLI - Generate code from specifications using AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add version argument
    parser.add_argument("--version", action="version", version=f"Blueprint CLI v{__version__}")

    # Required arguments
    parser.add_argument("--project-spec", required=True, help="Path to the project specification file")

    # Output options
    parser.add_argument("--output-dir", default="output", help="Output directory for generated files")
    parser.add_argument("--target-project", default="generated_project", help="Name of the target project")

    # Processing options
    parser.add_argument("--model", default="openai:o3-mini", help="LLM model to use for generation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--max-recursion-depth", type=int, default=3, help="Maximum recursion depth for component splitting"
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Blueprint CLI tool.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Parse arguments
    parsed_args = parse_args(args)

    # Setup logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Blueprint CLI v{__version__}")

    # Create configuration
    try:
        config = create_config_from_args(parsed_args)
        logger.debug(f"Configuration: {config}")

        if config.context_files:
            logger.info(f"Found {len(config.context_files)} context files in project spec")
        if config.reference_docs:
            logger.info(f"Found {len(config.reference_docs)} reference docs in project spec")
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        return 1

    # Ensure project_spec exists
    if not os.path.exists(config.project_spec):
        logger.error(f"Project specification file not found: {config.project_spec}")
        return 1

    # Ensure output directory exists
    try:
        ensure_directory(config.output_dir)
        logger.debug(f"Output directory: {config.output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        return 1

    # Run the project analysis
    try:
        logger.info("Analyzing project specification...")
        result = analyze_project(config)

        if result["needs_splitting"]:
            logger.info("Project needs to be split into components")

            # Set recursion limit based on CLI argument
            sys.setrecursionlimit(max(1000, parsed_args.max_recursion_depth * 2))

            # Recursively split the project
            final_components = split_project_recursively(config, result)

            logger.info(f"Recursive splitting complete, produced {len(final_components)} final components")

            # Write a summary of the final components
            summary_path = os.path.join(config.output_dir, "final_components_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                import json

                json.dump(final_components, f, indent=2)

            logger.info(f"Final components summary written to {summary_path}")
        else:
            logger.info("Project is small enough to process as a single component")
            # TODO: Implement single component processing

        logger.info("Blueprint generation completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Blueprint generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
