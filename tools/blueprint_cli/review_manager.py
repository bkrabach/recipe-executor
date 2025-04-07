"""
Review manager module for the Blueprint CLI tool.

This module handles preparing files for human review and processing
feedback after human review.
"""

import logging
import os
import shutil
from typing import Dict, Optional, Union

from component_evaluator import evaluate_spec

# Local imports
from config import ProjectConfig
from utils import ensure_directory

logger = logging.getLogger(__name__)


def prepare_for_review(
    component_id: str,
    original_spec_path: str,
    revised_spec_path: str,
    evaluation_path: str,
    questions_path: str,
    output_dir: str,
) -> str:
    """
    Prepare files for human review of a component.

    Args:
        component_id: ID of the component
        original_spec_path: Path to the original specification file
        revised_spec_path: Path to the revised specification file
        evaluation_path: Path to the evaluation file
        questions_path: Path to the questions file
        output_dir: Output directory for generated files

    Returns:
        Path to the human review directory

    Raises:
        Exception: If preparation fails
    """
    logger.info(f"Preparing human review for component: {component_id}")

    # Create human review directory
    review_dir = os.path.join(output_dir, "human_review")
    ensure_directory(review_dir)

    # Copy files to review directory
    review_files = [
        (original_spec_path, f"{component_id}_original_spec.md"),
        (revised_spec_path, f"{component_id}_revised_spec.md"),
        (evaluation_path, f"{component_id}_evaluation.md"),
        (questions_path, f"{component_id}_questions.md"),
    ]

    for src_path, dst_name in review_files:
        if src_path and os.path.exists(src_path):
            dst_path = os.path.join(review_dir, dst_name)
            try:
                shutil.copy2(src_path, dst_path)
                logger.debug(f"Copied {src_path} to {dst_path}")
            except Exception as e:
                logger.warning(f"Failed to copy {src_path} to {dst_path}: {e}")

    # Create a review summary file
    summary_path = os.path.join(review_dir, f"{component_id}_review_summary.md")
    summary_content = f"""# Human Review Required: {component_id}

## Component Information
- Component ID: {component_id}
- Original Specification: [{component_id}_original_spec.md]({component_id}_original_spec.md)
- Revised Specification: [{component_id}_revised_spec.md]({component_id}_revised_spec.md)
- Clarification Questions: [{component_id}_questions.md]({component_id}_questions.md)
- Evaluation Results: [{component_id}_evaluation.md]({component_id}_evaluation.md)

## Review Instructions
1. Review the original specification
2. Review the clarification questions generated
3. Review the revised specification
4. Review the evaluation results
5. Make any necessary changes to the revised specification file
6. When ready, return the updated specification to continue the pipeline
"""

    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
        logger.info(f"Created review summary at {summary_path}")
    except Exception as e:
        logger.error(f"Failed to write review summary: {e}")

    return review_dir


def process_feedback(
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

    # Create output directories
    clarification_dir = os.path.join(output_dir, "clarification")
    evaluation_dir = os.path.join(output_dir, "evaluation")
    ensure_directory(clarification_dir)
    ensure_directory(evaluation_dir)

    # Copy the updated spec to the clarification directory
    revised_spec_path = os.path.join(clarification_dir, f"{component_id}_candidate_spec_revised.md")

    try:
        shutil.copy2(updated_spec_path, revised_spec_path)
        logger.info(f"Copied updated spec to {revised_spec_path}")
    except Exception as e:
        logger.error(f"Failed to copy updated spec: {e}")
        raise Exception(f"Failed to copy updated spec for component {component_id}: {e}")

    # Re-evaluate the updated specification
    try:
        eval_result = evaluate_spec(component_id, revised_spec_path, config, evaluation_dir)
        logger.info(f"Re-evaluated specification after human review: {eval_result['status']}")
    except Exception as e:
        logger.error(f"Failed to re-evaluate specification: {e}")
        return {
            "component_id": component_id,
            "updated_spec": revised_spec_path,
            "status": "error",
            "error": f"Evaluation failed: {e}",
            "needs_review": True,
        }

    return {
        "component_id": component_id,
        "updated_spec": revised_spec_path,
        "evaluation": eval_result["path"],
        "status": eval_result["status"],
        "needs_review": eval_result["needs_review"],
    }


def create_review_form(
    component_id: str,
    spec_path: str,
    evaluation_path: str,
    template_path: Optional[str] = None,
    output_dir: str = "output",
) -> str:
    """
    Create a human review form for a component.

    This generates a structured form with checkboxes and comment fields
    to make the human review process more systematic.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification
        evaluation_path: Path to the evaluation results
        template_path: Optional path to a review form template
        output_dir: Output directory

    Returns:
        Path to the created review form
    """
    logger.info(f"Creating review form for component: {component_id}")

    # Create review directory
    review_dir = os.path.join(output_dir, "human_review")
    ensure_directory(review_dir)

    # Define form path
    form_path = os.path.join(review_dir, f"{component_id}_review_form.md")

    # Default form content
    form_content = f"""# Component Review Form: {component_id}

## Review Information
- Reviewer Name: _________________________
- Review Date: _________________________

## Component Assessment

Please check all that apply and provide comments for any areas that need improvement.

### Purpose and Scope
- [ ] Purpose is clearly defined
- [ ] Scope boundaries are well-established
- [ ] Responsibilities are appropriate
- **Comments:** _________________________

### Requirements Completeness
- [ ] All functional requirements are specified
- [ ] Non-functional requirements are addressed
- [ ] Edge cases are considered
- **Comments:** _________________________

### Implementation Guidance
- [ ] Implementation approach is clear
- [ ] Technical constraints are specified
- [ ] Architecture fit is appropriate
- **Comments:** _________________________

### Dependencies and Integration
- [ ] Dependencies are properly identified
- [ ] Integration points are well-defined
- [ ] Interfaces are clearly specified
- **Comments:** _________________________

### Overall Assessment
- [ ] Ready for implementation as-is
- [ ] Ready with minor revisions (noted above)
- [ ] Requires significant revision before implementation
- [ ] Needs to be reconsidered or redesigned
- **Comments:** _________________________

## Additional Notes
_________________________
_________________________
_________________________

## Recommended Changes
Please list specific changes recommended for this component specification:

1. _________________________
2. _________________________
3. _________________________
"""

    # If template provided, use it
    if template_path and os.path.exists(template_path):
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Replace placeholders
            form_content = template_content.replace("{{component_id}}", component_id)
        except Exception as e:
            logger.error(f"Failed to read template: {e}")
            # Form content already has default value

    # Write the form
    try:
        with open(form_path, "w", encoding="utf-8") as f:
            f.write(form_content)
        logger.info(f"Created review form at {form_path}")
        return form_path
    except Exception as e:
        logger.error(f"Failed to write review form: {e}")
        raise Exception(f"Failed to create review form for component {component_id}: {e}")
