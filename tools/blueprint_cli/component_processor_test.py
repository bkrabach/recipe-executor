#!/usr/bin/env python3
"""
Test script for the component processor module.

This script demonstrates how to use the component processor module
with a sample component specification.
"""

import argparse
import logging
import os
import sys
from typing import Dict

# Add the parent directory to the path to make blueprint_cli importable
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import blueprint_cli modules
# Import from the component_processor package

from answer_processor import generate_answers, generate_answers_from_template
from component_evaluator import evaluate_spec, evaluate_spec_locally
from component_processor import process_component, process_human_review_feedback
from config import ProjectConfig

# For mock implementations
from question_generator import generate_questions, generate_questions_from_template
from review_manager import create_review_form, prepare_for_review, process_feedback
from utils import ensure_directory, setup_logging


def create_sample_spec(output_dir: str) -> str:
    """
    Create a sample component specification for testing.

    Args:
        output_dir: Directory to create the sample spec in

    Returns:
        Path to the created specification file
    """
    ensure_directory(output_dir)

    # Simple but incomplete specification
    spec_content = """# Database Manager Component

## Overview
This component is responsible for database access and management.

## Features
- Connect to various database types
- Execute queries
- Manage transactions
- Handle connection pooling
"""

    # Write the specification file
    spec_path = os.path.join(output_dir, "database_manager_candidate_spec.md")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    return spec_path


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the test script.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Test the component processor module")

    parser.add_argument(
        "--output-dir",
        default="test_output",
        help="Output directory for test files",
    )

    parser.add_argument(
        "--model",
        default="openai:o3-mini",
        help="LLM model to use (if testing with real recipes)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementations instead of real recipe executor",
    )

    parser.add_argument(
        "--step",
        choices=["questions", "answers", "evaluate", "review", "all"],
        default="all",
        help="Which step(s) to test",
    )

    parser.add_argument(
        "--spec-path",
        help="Path to an existing component specification to use",
    )

    return parser.parse_args()


def test_question_generation(config: ProjectConfig, spec_path: str, mock: bool = False) -> str:
    """
    Test generating clarification questions.

    Args:
        config: Project configuration
        spec_path: Path to the component specification
        mock: Whether to use mock implementation

    Returns:
        Path to the generated questions file
    """
    print("\n=== Testing Question Generation ===")

    component_id = os.path.basename(spec_path).split("_")[0]
    clarification_dir = os.path.join(config.output_dir, "clarification")

    if mock:
        print("Using mock question generator...")
        questions_path = generate_questions_from_template(component_id, spec_path, output_dir=clarification_dir)
    else:
        print("Using recipe-based question generator...")
        questions_path = generate_questions(component_id, spec_path, config, clarification_dir)

    print(f"Generated questions at: {questions_path}")
    return questions_path


def test_answer_generation(config: ProjectConfig, spec_path: str, questions_path: str, mock: bool = False) -> str:
    """
    Test generating answers and a revised specification.

    Args:
        config: Project configuration
        spec_path: Path to the original specification
        questions_path: Path to the questions file
        mock: Whether to use mock implementation

    Returns:
        Path to the revised specification file
    """
    print("\n=== Testing Answer Generation ===")

    component_id = os.path.basename(spec_path).split("_")[0]
    clarification_dir = os.path.join(config.output_dir, "clarification")

    if mock:
        print("Using mock answer generator...")

        # Sample answers to questions
        answers = {
            "What is the primary responsibility of this component?": "The primary responsibility is to provide a unified interface for database operations, "
            "abstracting away the details of different database systems.",
            "What are the inputs and outputs?": "Inputs include connection parameters, SQL queries, and parameters. "
            "Outputs include query results, success/failure indicators, and error messages.",
            "What are the dependencies?": "This component depends on database drivers for supported databases "
            "and a configuration component for connection settings.",
        }

        revised_spec_path = generate_answers_from_template(
            component_id, spec_path, questions_path, answers, output_dir=clarification_dir
        )
    else:
        print("Using recipe-based answer generator...")
        revised_spec_path = generate_answers(component_id, spec_path, questions_path, config, clarification_dir)

    print(f"Generated revised specification at: {revised_spec_path}")
    return revised_spec_path


def test_evaluation(config: ProjectConfig, revised_spec_path: str, mock: bool = False) -> Dict:
    """
    Test evaluating a component specification.

    Args:
        config: Project configuration
        revised_spec_path: Path to the revised specification
        mock: Whether to use mock implementation

    Returns:
        Evaluation results
    """
    print("\n=== Testing Specification Evaluation ===")

    component_id = os.path.basename(revised_spec_path).split("_")[0]
    evaluation_dir = os.path.join(config.output_dir, "evaluation")

    if mock:
        print("Using mock evaluator...")

        # Define checklist for evaluation
        checklist = ["Purpose", "Core Requirements", "Implementation", "Component Dependencies", "Error Handling"]

        eval_result = evaluate_spec_locally(component_id, revised_spec_path, checklist, output_dir=evaluation_dir)
    else:
        print("Using recipe-based evaluator...")
        eval_result = evaluate_spec(component_id, revised_spec_path, config, evaluation_dir)

    print(f"Evaluation results: {eval_result}")
    return eval_result


def test_review_preparation(
    config: ProjectConfig, spec_path: str, revised_spec_path: str, eval_result: Dict, questions_path: str
) -> str:
    """
    Test preparing files for human review.

    Args:
        config: Project configuration
        spec_path: Path to the original specification
        revised_spec_path: Path to the revised specification
        eval_result: Evaluation results
        questions_path: Path to the questions file

    Returns:
        Path to the review directory
    """
    print("\n=== Testing Human Review Preparation ===")

    component_id = os.path.basename(spec_path).split("_")[0]

    review_dir = prepare_for_review(
        component_id, spec_path, revised_spec_path, eval_result["path"], questions_path, config.output_dir
    )

    # Create a review form
    form_path = create_review_form(component_id, revised_spec_path, eval_result["path"], output_dir=config.output_dir)

    print(f"Prepared review files in: {review_dir}")
    print(f"Created review form at: {form_path}")

    # For demo purposes, create a mock updated spec
    updated_spec_content = """# Database Manager Component

## Purpose
The primary responsibility is to provide a unified interface for database operations, abstracting away the details of different database systems.

## Core Requirements
- Connect to various database types (MySQL, PostgreSQL, SQLite)
- Execute queries with parameter binding
- Manage transactions with commit/rollback
- Handle connection pooling for performance
- Provide logging of database operations

## Implementation Considerations
- Use adapter pattern for different database systems
- Implement connection pooling for efficiency
- Provide both synchronous and asynchronous interfaces
- Use prepared statements for security

## Component Dependencies
- Database drivers for each supported database type
- Configuration component for connection settings
- Logging component for operation logging

## Error Handling
- Standardize error responses across database types
- Implement retry logic for transient errors
- Provide detailed error messages with error codes
- Support transaction rollback on errors

## Future Considerations
- Add support for NoSQL databases
- Implement query builder interface
- Add database migration tools
"""

    updated_spec_path = os.path.join(review_dir, f"{component_id}_updated_spec.md")
    with open(updated_spec_path, "w", encoding="utf-8") as f:
        f.write(updated_spec_content)

    print(f"Created mock updated specification at: {updated_spec_path}")
    return updated_spec_path


def test_feedback_processing(config: ProjectConfig, component_id: str, updated_spec_path: str) -> Dict:
    """
    Test processing human review feedback.

    Args:
        config: Project configuration
        component_id: ID of the component
        updated_spec_path: Path to the updated specification

    Returns:
        Processing results
    """
    print("\n=== Testing Feedback Processing ===")

    feedback_result = process_feedback(component_id, updated_spec_path, config, config.output_dir)

    print(f"Feedback processing results: {feedback_result}")
    return feedback_result


def test_entire_pipeline(config: ProjectConfig, spec_path: str, mock: bool = False):
    """
    Test the entire component processing pipeline.

    Args:
        config: Project configuration
        spec_path: Path to the component specification
        mock: Whether to use mock implementations
    """
    print("\n=== Testing Complete Processing Pipeline ===")

    component_id = os.path.basename(spec_path).split("_")[0]

    # Process the component
    result = process_component(component_id, spec_path, config, config.output_dir)

    print(f"Component processing results: {result}")

    # If the component needs review, process feedback
    if result.get("needs_review", False):
        print("\nComponent needs human review")

        # Create a mock updated spec for testing
        review_dir = os.path.join(config.output_dir, "human_review")
        ensure_directory(review_dir)

        updated_spec_content = """# Database Manager Component

## Purpose
The primary responsibility is to provide a unified interface for database operations, abstracting away the details of different database systems.

## Core Requirements
- Connect to various database types (MySQL, PostgreSQL, SQLite)
- Execute queries with parameter binding
- Manage transactions with commit/rollback
- Handle connection pooling for performance
- Provide logging of database operations

## Implementation Considerations
- Use adapter pattern for different database systems
- Implement connection pooling for efficiency
- Provide both synchronous and asynchronous interfaces
- Use prepared statements for security

## Component Dependencies
- Database drivers for each supported database type
- Configuration component for connection settings
- Logging component for operation logging

## Error Handling
- Standardize error responses across database types
- Implement retry logic for transient errors
- Provide detailed error messages with error codes
- Support transaction rollback on errors

## Future Considerations
- Add support for NoSQL databases
- Implement query builder interface
- Add database migration tools
"""

        updated_spec_path = os.path.join(review_dir, f"{component_id}_updated_spec.md")
        with open(updated_spec_path, "w", encoding="utf-8") as f:
            f.write(updated_spec_content)

        print(f"Created mock updated specification at: {updated_spec_path}")

        # Process the feedback
        feedback_result = process_human_review_feedback(component_id, updated_spec_path, config, config.output_dir)

        print(f"Feedback processing results: {feedback_result}")


def main():
    """Main entry point for the test script."""
    # Parse arguments
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    # Create output directory
    ensure_directory(args.output_dir)

    # Create a configuration
    config = ProjectConfig(
        project_spec="test_project_spec.md",  # Not actually used in this test
        output_dir=args.output_dir,
        model=args.model,
        verbose=args.verbose,
    )

    # Determine the spec path
    if args.spec_path and os.path.exists(args.spec_path):
        spec_path = args.spec_path
        print(f"Using specified specification: {spec_path}")
    else:
        spec_path = create_sample_spec(args.output_dir)
        print(f"Created sample specification: {spec_path}")

    # Get component ID from spec path
    component_id = os.path.basename(spec_path).split("_")[0]

    # Test the specified step(s)
    if args.step == "questions" or args.step == "all":
        questions_path = test_question_generation(config, spec_path, args.mock)
    else:
        # Skip but set a default path for later steps
        questions_path = os.path.join(
            args.output_dir, "clarification", f"{component_id}_component_clarification_questions.md"
        )

    if args.step == "answers" or args.step == "all":
        # Ensure we have questions to use
        if not os.path.exists(questions_path) and args.step == "answers":
            questions_path = test_question_generation(config, spec_path, args.mock)

        revised_spec_path = test_answer_generation(config, spec_path, questions_path, args.mock)
    else:
        # Skip but set a default path for later steps
        revised_spec_path = os.path.join(args.output_dir, "clarification", f"{component_id}_candidate_spec_revised.md")

    if args.step == "evaluate" or args.step == "all":
        # Ensure we have a revised spec to evaluate
        if not os.path.exists(revised_spec_path) and args.step == "evaluate":
            if not os.path.exists(questions_path):
                questions_path = test_question_generation(config, spec_path, args.mock)
            revised_spec_path = test_answer_generation(config, spec_path, questions_path, args.mock)

        eval_result = test_evaluation(config, revised_spec_path, args.mock)
    else:
        # Skip but set a default result for later steps
        eval_result = {
            "status": "needs_clarification",
            "path": os.path.join(args.output_dir, "evaluation", f"{component_id}_needs_clarification.md"),
            "needs_review": True,
        }

    if args.step == "review" or args.step == "all":
        # Ensure we have all the files needed for review
        if not os.path.exists(revised_spec_path) and args.step == "review":
            if not os.path.exists(questions_path):
                questions_path = test_question_generation(config, spec_path, args.mock)
            revised_spec_path = test_answer_generation(config, spec_path, questions_path, args.mock)
            eval_result = test_evaluation(config, revised_spec_path, args.mock)

        updated_spec_path = test_review_preparation(config, spec_path, revised_spec_path, eval_result, questions_path)
        # Store the result but don't use it - this avoids the unused variable warning
        _ = test_feedback_processing(config, component_id, updated_spec_path)

    if args.step == "all":
        # Test the entire pipeline as a single integrated flow
        print("\n\n=== NOW TESTING THE ENTIRE PIPELINE AS A UNIFIED FLOW ===")
        # Create a fresh sample spec to avoid interference from earlier tests
        fresh_spec_path = create_sample_spec(os.path.join(args.output_dir, "pipeline_test"))
        config.output_dir = os.path.join(args.output_dir, "pipeline_test")
        test_entire_pipeline(config, fresh_spec_path, args.mock)

    print("\n=== Test Completed Successfully ===")


if __name__ == "__main__":
    main()
