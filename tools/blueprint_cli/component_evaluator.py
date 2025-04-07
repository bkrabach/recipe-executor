"""
Component evaluator module for the Blueprint CLI tool.

This module handles evaluating component specifications to determine
if they are ready for implementation or need further refinement.
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory

logger = logging.getLogger(__name__)


def evaluate_spec(
    component_id: str, spec_path: str, config: ProjectConfig, output_dir: str
) -> Dict[str, Union[str, bool]]:
    """
    Evaluate a component specification to determine if it's ready for implementation.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification file
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Dict with evaluation results (status, path to evaluation file, needs_review flag)

    Raises:
        Exception: If evaluation fails
    """
    logger.info(f"Evaluating specification for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define expected output file paths
    needs_clarification_path = os.path.join(output_dir, f"{component_id}_needs_clarification.md")
    evaluation_summary_path = os.path.join(output_dir, f"{component_id}_evaluation_summary.md")

    # Check if output already exists (for resuming)
    if os.path.exists(needs_clarification_path):
        logger.info(f"Evaluation (needs clarification) already exists for {component_id}")
        return {
            "status": "needs_clarification",
            "path": needs_clarification_path,
            "needs_review": True,
        }
    elif os.path.exists(evaluation_summary_path):
        logger.info(f"Evaluation (passed) already exists for {component_id}")
        return {
            "status": "passed",
            "path": evaluation_summary_path,
            "needs_review": False,
        }

    # Set up context for the recipe
    context = {
        "candidate_spec_path": spec_path,
        "component_id": component_id,
        "output_root": output_dir,
        "model": config.model,
    }

    # Get recipe path
    recipe_path = get_recipe_path("evaluate_candidate_spec.json")

    # Run the recipe
    logger.info(f"Running evaluation with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error(f"Failed to evaluate specification for {component_id}")
        raise Exception(f"Evaluation failed for component {component_id}")

    # Determine evaluation result
    if os.path.exists(needs_clarification_path):
        logger.info(f"Component {component_id} needs clarification")
        return {
            "status": "needs_clarification",
            "path": needs_clarification_path,
            "needs_review": True,
        }
    elif os.path.exists(evaluation_summary_path):
        logger.info(f"Component {component_id} passed evaluation")
        return {
            "status": "passed",
            "path": evaluation_summary_path,
            "needs_review": False,
        }
    else:
        logger.error(f"No evaluation file found for component {component_id}")
        raise Exception(f"Evaluation file not found for component {component_id}")


def evaluate_spec_locally(
    component_id: str, spec_path: str, checklist: Optional[List[str]] = None, output_dir: str = "output"
) -> Dict[str, Union[str, bool]]:
    """
    Perform a basic local evaluation of a component specification.

    This is a simpler alternative to using the recipe-based evaluation
    when testing or when the recipe executor is not available.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification file
        checklist: Optional list of required sections to check for
        output_dir: Output directory for generated files

    Returns:
        Dict with evaluation results
    """
    logger.info(f"Performing local evaluation for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Default checklist of required sections
    if checklist is None:
        checklist = ["Purpose", "Core Requirements", "Implementation", "Component Dependencies", "Error Handling"]

    # Read the spec file
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            spec_content = f.read()
    except Exception as e:
        logger.error(f"Failed to read specification: {e}")
        raise Exception(f"Failed to read specification for component {component_id}")

    # Check for required sections
    missing_sections = []
    for section in checklist:
        # Look for section headers (e.g., ## Purpose, ## Core Requirements)
        if not re.search(r"#{1,3}\s+{section}", spec_content, re.IGNORECASE):
            missing_sections.append(section)

    # Determine if the spec passes or needs clarification
    if missing_sections:
        status = "needs_clarification"
        needs_review = True
        missing_sections_text = "".join([f"- {section}\n" for section in missing_sections])
        eval_content = f"""# Evaluation: Component {component_id} Needs Clarification

## Missing Sections
The following required sections are missing from the specification:

{missing_sections_text}

## Recommendation
Please update the specification to include these sections.
"""
        output_path = os.path.join(output_dir, f"{component_id}_needs_clarification.md")
    else:
        status = "passed"
        needs_review = False
        sections_verified_text = "".join([f"- {section}\\n" for section in checklist])
        eval_content = f"""# Evaluation: Component {component_id} Passed

All required sections are present in the specification.

## Sections Verified
{sections_verified_text}

## Recommendation
This component is ready for blueprint generation.
"""
        output_path = os.path.join(output_dir, f"{component_id}_evaluation_summary.md")

    # Write the evaluation file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(eval_content)
        logger.info(f"Evaluation written to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write evaluation: {e}")
        raise Exception(f"Failed to write evaluation for component {component_id}")

    return {
        "status": status,
        "path": output_path,
        "needs_review": needs_review,
    }


def parse_evaluation_results(evaluation_path: str) -> Dict[str, Any]:
    """
    Parse an evaluation file to extract scores and recommendations.

    Args:
        evaluation_path: Path to the evaluation file

    Returns:
        Dict with parsed evaluation results
    """
    logger.debug(f"Parsing evaluation results from {evaluation_path}")

    try:
        with open(evaluation_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read evaluation file: {e}")
        return {"average_score": 0, "needs_review": True}

    # Extract scores (typically in format "score: X/5" or similar)
    scores = re.findall(r"score:\s*(\d+)(?:/\d+)?", content, re.IGNORECASE)
    scores = [int(score) for score in scores if score]

    # Calculate average score if scores found
    average_score = sum(scores) / len(scores) if scores else 0

    # Determine if review is needed (if "needs clarification" is in the filename)
    needs_review = "needs_clarification" in os.path.basename(evaluation_path).lower()

    # Extract major issues
    issues = []
    issues_section = re.search(r"(?:Issues|Problems|Concerns):(.*?)(?:##|\Z)", content, re.DOTALL | re.IGNORECASE)
    if issues_section:
        # Extract bullet points from issues section
        issue_points = re.findall(r"[-*]\s*(.*?)(?:\n|$)", issues_section.group(1))
        issues = [issue.strip() for issue in issue_points if issue.strip()]

    return {
        "average_score": average_score,
        "scores": scores,
        "needs_review": needs_review,
        "issues": issues,
    }
