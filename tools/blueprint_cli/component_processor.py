"""
Component processor module for the Blueprint CLI tool.

This module orchestrates the processing of component specifications,
including generating clarification questions, processing answers,
and evaluating component readiness.
"""

import logging
import os
from typing import Dict, List, Tuple, Union

# Import specialized processors
import answer_processor
import component_evaluator
import question_generator
import review_manager

# Local imports
from config import ProjectConfig
from utils import ensure_directory

logger = logging.getLogger(__name__)


def process_component(
    component_id: str,
    spec_path: str,
    config: ProjectConfig,
    output_dir: str,
) -> Dict[str, Union[str, bool]]:
    """
    Process a component through the clarification and evaluation workflow.

    Args:
        component_id: ID of the component to process
        spec_path: Path to the component specification file
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Dict with processing results (status, paths to generated files, etc.)

    Raises:
        Exception: If processing fails
    """
    logger.info(f"Processing component: {component_id}")

    # Create output directories
    clarification_dir = os.path.join(output_dir, "clarification")
    evaluation_dir = os.path.join(output_dir, "evaluation")
    ensure_directory(clarification_dir)
    ensure_directory(evaluation_dir)

    # Step 1: Generate clarification questions
    try:
        questions_path = question_generator.generate_questions(component_id, spec_path, config, clarification_dir)
        logger.info(f"Generated clarification questions for {component_id}")
    except Exception as e:
        logger.error(f"Failed to generate clarification questions: {e}")
        return {
            "component_id": component_id,
            "original_spec": spec_path,
            "status": "error",
            "error": f"Question generation failed: {e}",
            "needs_review": True,
        }

    # Step 2: Generate answers and revised specification
    try:
        revised_spec_path = answer_processor.generate_answers(
            component_id, spec_path, questions_path, config, clarification_dir
        )
        logger.info(f"Generated revised specification for {component_id}")
    except Exception as e:
        logger.error(f"Failed to generate answers: {e}")
        return {
            "component_id": component_id,
            "original_spec": spec_path,
            "questions": questions_path,
            "status": "error",
            "error": f"Answer generation failed: {e}",
            "needs_review": True,
        }

    # Step 3: Evaluate the revised specification
    try:
        eval_result = component_evaluator.evaluate_spec(component_id, revised_spec_path, config, evaluation_dir)
        logger.info(f"Evaluated specification for {component_id}: {eval_result['status']}")
    except Exception as e:
        logger.error(f"Failed to evaluate specification: {e}")
        return {
            "component_id": component_id,
            "original_spec": spec_path,
            "questions": questions_path,
            "revised_spec": revised_spec_path,
            "status": "error",
            "error": f"Evaluation failed: {e}",
            "needs_review": True,
        }

    # Return processing results
    return {
        "component_id": component_id,
        "original_spec": spec_path,
        "questions": questions_path,
        "revised_spec": revised_spec_path,
        "evaluation": eval_result["path"],
        "status": eval_result["status"],
        "needs_review": eval_result["needs_review"],
    }


def batch_process_components(
    component_specs: List[Tuple[str, str]],
    config: ProjectConfig,
    output_dir: str,
) -> Dict[str, Dict[str, Union[str, bool]]]:
    """
    Process multiple components in sequence.

    Args:
        component_specs: List of (component_id, spec_path) tuples
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Dict mapping component_id to processing results

    Raises:
        Exception: If processing fails
    """
    logger.info(f"Batch processing {len(component_specs)} components")

    results = {}

    for component_id, spec_path in component_specs:
        try:
            result = process_component(component_id, spec_path, config, output_dir)
            results[component_id] = result
        except Exception as e:
            logger.error(f"Failed to process component {component_id}: {e}")
            results[component_id] = {
                "component_id": component_id,
                "original_spec": spec_path,
                "status": "error",
                "error": str(e),
                "needs_review": True,
            }

    # Prepare human review for components that need it
    review_components = {}
    for component_id, result in results.items():
        if result.get("needs_review", False):
            try:
                review_dir = review_manager.prepare_for_review(
                    component_id,
                    result.get("original_spec", ""),
                    result.get("revised_spec", ""),
                    result.get("evaluation", ""),
                    result.get("questions", ""),
                    output_dir,
                )
                review_components[component_id] = review_dir
            except Exception as e:
                logger.error(f"Failed to prepare human review for component {component_id}: {e}")

    if review_components:
        logger.info(f"{len(review_components)} components need human review")

    return results


def process_human_review_feedback(
    component_id: str,
    updated_spec_path: str,
    config: ProjectConfig,
    output_dir: str,
) -> Dict[str, Union[str, bool]]:
    """
    Process human review feedback for a component.

    Args:
        component_id: ID of the component
        updated_spec_path: Path to the updated specification after human review
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Dict with processing results

    Raises:
        Exception: If processing fails
    """
    logger.info(f"Processing human review feedback for component: {component_id}")

    # Process the feedback and re-evaluate the component
    return review_manager.process_feedback(component_id, updated_spec_path, config, output_dir)
