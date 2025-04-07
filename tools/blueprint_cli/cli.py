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
from typing import Any, Dict, List, Optional

# Import local modules using relative paths based on script location
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Local imports
from analyzer import analyze_project  # noqa: E402
from config import ProjectConfig, create_config_from_args  # noqa: E402
from splitter import split_project_recursively  # noqa: E402
from utils import ensure_directory, pause_for_user, setup_logging  # noqa: E402

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
        "--auto-run", action="store_true", dest="auto_run", help="Automatically run all steps without pausing between"
    )
    parser.add_argument(
        "--max-recursion-depth", type=int, default=3, help="Maximum recursion depth for component splitting"
    )

    # Component processing options
    parser.add_argument("--skip-processing", action="store_true", help="Skip the component processing phase")
    parser.add_argument("--process-review", help="Process human review feedback for a component (provide component ID)")
    parser.add_argument("--review-path", help="Path to the updated spec from human review (used with --process-review)")
    parser.add_argument("--component-filter", help="Only process components matching this prefix")

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

    # Handle processing human review feedback
    if parsed_args.process_review:
        component_id = parsed_args.process_review
        review_path = parsed_args.review_path

        if not review_path:
            logger.error("--review-path is required when using --process-review")
            return 1

        if not os.path.exists(review_path):
            logger.error(f"Review path not found: {review_path}")
            return 1

        logger.info(f"Processing human review feedback for component: {component_id}")

        # Import component_processor here to avoid circular imports
        from component_processor import process_human_review_feedback

        try:
            result = process_human_review_feedback(component_id, review_path, config, config.output_dir)

            logger.info(f"Feedback processing result: {result}")

            if result.get("needs_review", False):
                logger.info(f"Component {component_id} still needs review after processing feedback")
            else:
                logger.info(f"Component {component_id} is now ready after processing feedback")

            pause_for_user(config)

            return 0
        except Exception as e:
            logger.error(f"Failed to process human review feedback: {e}")
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

        pause_for_user(config)

        if result["needs_splitting"]:
            logger.info("Project needs to be split into components")

            # Set recursion limit based on CLI argument
            sys.setrecursionlimit(max(1000, parsed_args.max_recursion_depth * 2))

            # Recursively split the project
            final_components = split_project_recursively(config, result)

            logger.info(f"Loaded {len(final_components)} final components (resume-aware)")

            logger.info(f"Recursive splitting complete, produced {len(final_components)} final components")

            # Write a summary of the final components
            summary_path = os.path.join(config.output_dir, "final_components_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                import json

                json.dump(final_components, f, indent=2)

            logger.info(f"Final components summary written to {summary_path}")

            # Continue to component processing phase
            if not parsed_args.skip_processing:
                logger.info("Proceeding to component processing phase...")
                process_components(config, final_components)

        else:
            logger.info("Project is small enough to process as a single component")

            # Create a single component spec
            component_id = "main_component"
            spec_filename = f"{component_id}_spec.md"
            spec_path = os.path.join(config.output_dir, "components", spec_filename)

            # Process the single component if it exists
            if os.path.exists(spec_path) and not parsed_args.skip_processing:
                logger.info("Processing the single component...")
                single_component = [
                    {
                        "component_id": component_id,
                        "component_name": "Main Component",
                        "description": "Single component implementation",
                        "spec_file": spec_filename,
                        "dependencies": [],
                    }
                ]
                process_components(config, single_component)

        logger.info("Blueprint generation completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Blueprint generation failed: {e}")
        return 1


def process_components(config: ProjectConfig, components: List[Dict[str, Any]]) -> None:
    """
    Process component specifications through the clarification and evaluation workflow.

    Args:
        config: Project configuration
        components: List of component dictionaries from the splitting phase
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Processing {len(components)} components")

    # Check if we have existing evaluation files
    eval_dir = os.path.join(config.output_dir, "evaluation")
    if os.path.exists(eval_dir):
        eval_files = os.listdir(eval_dir)
        logger.info(f"Found {len(eval_files)} existing evaluation files: {eval_files}")

        # Extract component IDs from evaluation files
        processed_components = {}
        for filename in eval_files:
            if filename.endswith("_evaluation_summary.md"):
                component_id = filename.replace("_evaluation_summary.md", "")
                eval_path = os.path.join(eval_dir, filename)
                revised_spec_path = os.path.join(
                    config.output_dir, "clarification", f"{component_id}_candidate_spec_revised.md"
                )

                if os.path.exists(revised_spec_path):
                    # Read evaluation to check if it needs review
                    with open(eval_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        needs_review = "NEEDS FURTHER REVIEW: Yes" in content

                    processed_components[component_id] = {"needs_review": needs_review, "spec_path": revised_spec_path}
                    logger.debug(f"Found processed component: {component_id}, needs_review: {needs_review}")

        if processed_components:
            logger.info(f"Found {len(processed_components)} previously processed components")

            # Check if all components in the current run have already been processed
            all_processed = True
            for component in components:
                component_id = component["component_id"]
                if component_id not in processed_components:
                    all_processed = False
                    logger.debug(f"Component {component_id} has not been processed yet")

            if all_processed:
                logger.info("All components already processed, skipping to blueprint generation")

                needs_review = [comp_id for comp_id, result in processed_components.items() if result["needs_review"]]
                completed = [comp_id for comp_id, result in processed_components.items() if not result["needs_review"]]

                logger.info(f"Found {len(completed)} components ready, {len(needs_review)} need review")

                # Import blueprint generator
                from blueprint_generator import batch_generate_blueprints

                # Generate blueprints for completed components
                if completed:
                    logger.info(f"Generating blueprints for {len(completed)} ready components...")
                    try:
                        # Create component info dictionaries for blueprint generation
                        complete_components = []
                        for component in components:
                            if component["component_id"] in completed:
                                component_id = component["component_id"]
                                complete_components.append({
                                    "component_id": component_id,
                                    "revised_spec": processed_components[component_id]["spec_path"],
                                    "spec_file": component.get("spec_file", f"{component_id}_spec.md"),
                                })

                        blueprint_results = batch_generate_blueprints(complete_components, config, config.output_dir)
                        logger.info(f"Successfully generated blueprints for {len(blueprint_results)} components")
                    except Exception as e:
                        logger.error(f"Blueprint generation failed: {e}")

                return

    # Import component_processor here to avoid circular imports
    from component_processor import batch_process_components

    # Convert components to the format expected by batch_process_components
    component_specs = []
    for component in components:
        component_id = component["component_id"]
        spec_file = component["spec_file"]
        spec_path = os.path.join(config.output_dir, "components", spec_file)

        if os.path.exists(spec_path):
            component_specs.append((component_id, spec_path))
        else:
            logger.warning(f"Component specification not found: {spec_path}")

    if not component_specs:
        logger.error("No component specifications found to process")
        return

    # Process the components
    try:
        results = batch_process_components(component_specs, config, config.output_dir)

        # Check results
        needs_review = []
        completed = []

        for component_id, result in results.items():
            if result.get("needs_review", False):
                needs_review.append(component_id)
            else:
                completed.append(component_id)

        # Print summary
        logger.info(
            f"Component processing complete. {len(completed)} components ready, {len(needs_review)} need review"
        )

        if needs_review:
            logger.info("Components needing human review:")
            for component_id in needs_review:
                logger.info(f"  - {component_id}")

            logger.info(f"Please review these components in the {config.output_dir}/human_review directory")
            logger.info("After review, you can run the CLI again with the --process-review flag")

        # Import blueprint generator
        from blueprint_generator import batch_generate_blueprints

        # Generate blueprints for completed components
        if completed:
            logger.info(f"Generating blueprints for {len(completed)} ready components...")
            try:
                blueprint_results = batch_generate_blueprints(
                    [c for c in components if c["component_id"] in completed], config, config.output_dir
                )
                logger.info(f"Successfully generated blueprints for {len(blueprint_results)} components")
            except Exception as e:
                logger.error(f"Blueprint generation failed: {e}")

    except Exception as e:
        logger.error(f"Component processing failed: {e}")


if __name__ == "__main__":
    sys.exit(main())
