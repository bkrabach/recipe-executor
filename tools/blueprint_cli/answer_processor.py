"""
Answer processor module for the Blueprint CLI tool.

This module handles generating answers to clarification questions and
producing revised component specifications.
"""

import logging
import os
from typing import Dict

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory

logger = logging.getLogger(__name__)


def generate_answers(
    component_id: str,
    spec_path: str,
    questions_path: str,
    config: ProjectConfig,
    output_dir: str,
) -> str:
    """
    Generate answers to clarification questions and a revised component specification.

    Args:
        component_id: ID of the component
        spec_path: Path to the original component specification file
        questions_path: Path to the clarification questions file
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Path to the revised specification file

    Raises:
        Exception: If answer generation fails
    """
    logger.info(f"Generating clarification answers for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define the expected output file path
    revised_spec_path = os.path.join(output_dir, f"{component_id}_candidate_spec_revised.md")

    # Check if output already exists (for resuming)
    if os.path.exists(revised_spec_path):
        logger.info(f"Revised specification already exists for {component_id}")
        return revised_spec_path

    # Format context files for recipe
    context_files = []
    if config.context_files:
        context_files = [item["path"] for item in config.context_files]
    context_files_str = ",".join(context_files)

    # Set up context for the recipe
    context = {
        "candidate_spec_path": spec_path,
        "clarification_questions_path": questions_path,
        "component_id": component_id,
        "output_root": output_dir,
        "model": config.model,
    }

    # Add context files if available
    if context_files_str:
        context["context_files"] = context_files_str

    # Get recipe path
    recipe_path = get_recipe_path("generate_clarification_answers.json")

    # Run the recipe
    logger.info(f"Running answer generation with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error(f"Failed to generate clarification answers for {component_id}")
        raise Exception(f"Answer generation failed for component {component_id}")

    # Check for revised specification file
    if not os.path.exists(revised_spec_path):
        logger.error(f"Revised specification file not found: {revised_spec_path}")
        raise Exception(f"Revised specification not found for component {component_id}")

    logger.info(f"Successfully generated revised specification for {component_id}")
    return revised_spec_path


def generate_answers_from_template(
    component_id: str, spec_path: str, questions_path: str, answers: Dict[str, str], output_dir: str = "output"
) -> str:
    """
    Generate a revised specification based on provided answers.

    This is a simpler alternative to using the recipe-based generation
    when testing or when the recipe executor is not available.

    Args:
        component_id: ID of the component
        spec_path: Path to the original component specification
        questions_path: Path to the clarification questions
        answers: Dictionary of question/answer pairs
        output_dir: Output directory for generated files

    Returns:
        Path to the revised specification file
    """
    logger.info(f"Generating revised specification with manual answers for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define the expected output file path
    revised_spec_path = os.path.join(output_dir, f"{component_id}_candidate_spec_revised.md")

    # Check if output already exists
    if os.path.exists(revised_spec_path):
        logger.info(f"Revised specification already exists for {component_id}")
        return revised_spec_path

    # Read the original spec
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            original_spec = f.read()
    except Exception as e:
        logger.error(f"Failed to read original specification: {e}")
        raise Exception(f"Failed to read original specification for component {component_id}")

    # Generate a revised spec with the answers
    answers_section = "## Clarification Answers\n\n"
    for question, answer in answers.items():
        answers_section += f"**Q: {question}**\n\n{answer}\n\n"

    revised_spec = f"{original_spec}\n\n{answers_section}"

    # Write the revised spec
    try:
        with open(revised_spec_path, "w", encoding="utf-8") as f:
            f.write(revised_spec)
        logger.info(f"Generated revised specification at {revised_spec_path}")
        return revised_spec_path
    except Exception as e:
        logger.error(f"Failed to write revised specification: {e}")
        raise Exception(f"Failed to write revised specification for component {component_id}")
