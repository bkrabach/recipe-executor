"""
Question generator module for the Blueprint CLI tool.

This module handles generating clarification questions for component specifications.
"""

import logging
import os
from typing import Optional

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory

logger = logging.getLogger(__name__)


def generate_questions(component_id: str, spec_path: str, config: ProjectConfig, output_dir: str) -> str:
    """
    Generate clarification questions for a component specification.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification file
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Path to the generated questions file

    Raises:
        Exception: If question generation fails
    """
    logger.info(f"Generating clarification questions for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define the expected output file path
    questions_path = os.path.join(output_dir, f"{component_id}_component_clarification_questions.md")

    # Check if output already exists (for resuming)
    if os.path.exists(questions_path):
        logger.info(f"Clarification questions already exist for {component_id}")
        return questions_path

    # Set up context for the recipe
    context = {
        "candidate_spec_path": spec_path,
        "component_id": component_id,
        "output_root": output_dir,
        "model": config.model,
    }

    # Get recipe path
    recipe_path = get_recipe_path("generate_clarification_questions.json")

    # Run the recipe
    logger.info(f"Running question generation with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error(f"Failed to generate clarification questions for {component_id}")
        raise Exception(f"Question generation failed for component {component_id}")

    # Check for generated questions file
    if not os.path.exists(questions_path):
        logger.error(f"Questions file not found: {questions_path}")
        raise Exception(f"Questions file not found for component {component_id}")

    logger.info(f"Successfully generated clarification questions for {component_id}")
    return questions_path


def generate_questions_from_template(
    component_id: str, spec_path: str, template_path: Optional[str] = None, output_dir: str = "output"
) -> str:
    """
    Generate clarification questions using a template.

    This is a simpler alternative to using the recipe-based generation
    when testing or when the recipe executor is not available.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification file
        template_path: Optional path to a question template file
        output_dir: Output directory for generated files

    Returns:
        Path to the generated questions file
    """
    logger.info(f"Generating clarification questions from template for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define the expected output file path
    questions_path = os.path.join(output_dir, f"{component_id}_component_clarification_questions.md")

    # Check if output already exists (for resuming)
    if os.path.exists(questions_path):
        logger.info(f"Clarification questions already exist for {component_id}")
        return questions_path

    # If no template provided, use a basic question template
    if not template_path or not os.path.exists(template_path):
        questions_content = f"""# Clarification Questions for {component_id}

## Introduction
These questions aim to clarify ambiguities and fill gaps in the component specification.

## Current Specification Summary
This component appears to handle [brief summary of component purpose].

## Key Areas Needing Clarification

### Purpose and Scope
1. What is the primary responsibility of this component?
2. What are the boundaries of this component (what's in scope vs. out of scope)?
3. Are there any specific constraints this component must operate within?

### Functional Requirements
1. What specific capabilities must this component provide?
2. What are the expected inputs and outputs for this component?
3. How should this component interact with its users or callers?

### Technical Requirements
1. Are there specific implementation technologies or approaches required?
2. What performance characteristics are expected for this component?
3. Are there any security considerations for this component?

### Integration and Dependencies
1. Which other components does this component depend on?
2. How does this component fit into the overall system architecture?
3. Are there external systems or services this component needs to integrate with?

### Error Handling and Edge Cases
1. What are the expected failure modes for this component?
2. How should errors be handled and reported?
3. Are there specific edge cases that need special handling?

## Next Steps
Please provide answers to these questions to help refine the component specification.
"""
    else:
        # Read the template file
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Replace placeholders in the template
            questions_content = template_content.replace("{{component_id}}", component_id)
        except Exception as e:
            logger.error(f"Failed to read template file: {e}")
            # Fallback to basic template
            questions_content = f"# Clarification Questions for {component_id}\n\n## Basic Questions\n1. What is the purpose of this component?\n2. What are the inputs and outputs?\n3. What are the dependencies?"

    # Write the questions file
    try:
        with open(questions_path, "w", encoding="utf-8") as f:
            f.write(questions_content)
        logger.info(f"Generated clarification questions at {questions_path}")
        return questions_path
    except Exception as e:
        logger.error(f"Failed to write questions file: {e}")
        raise Exception(f"Failed to write questions file for component {component_id}")
