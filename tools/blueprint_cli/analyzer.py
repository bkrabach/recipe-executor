"""
Project analyzer module for the Blueprint CLI tool.

This module provides functions for analyzing project specifications
to determine if they need to be split into components.
"""

import json
import logging
import os
from typing import Dict, Union

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory, format_files_for_recipe

logger = logging.getLogger(__name__)


def analyze_project(config: ProjectConfig) -> Dict[str, Union[bool, str]]:
    """
    Analyze a project specification to determine if it needs to be split.

    Args:
        config: Project configuration

    Returns:
        Dictionary with analysis results

    Raises:
        Exception: If analysis fails
    """
    # Create output directories
    analysis_dir = os.path.join(config.output_dir, "analysis")
    ensure_directory(analysis_dir)

    # Format context files for recipe
    context_files_str = format_files_for_recipe(config.context_files)

    # Set up context for the recipe
    context = {"input": config.project_spec, "output_root": analysis_dir, "model": config.model}

    # Add context files if available
    if context_files_str:
        context["files"] = context_files_str

    # Get recipe path
    recipe_path = get_recipe_path("analyze_project.json")

    # Run the recipe
    logger.info(f"Running project analysis with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error("Project analysis failed")
        raise Exception("Project analysis failed")

    # Check for analysis result file
    analysis_file = os.path.join(analysis_dir, "project_analysis_result.json")
    if not os.path.exists(analysis_file):
        logger.error(f"Analysis result file not found: {analysis_file}")
        raise Exception("Analysis result file not found")

    # Load analysis result
    try:
        with open(analysis_file, "r") as f:
            result = json.load(f)

        logger.info(f"Analysis result: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to load analysis result: {e}")
        raise Exception(f"Failed to load analysis result: {e}")
