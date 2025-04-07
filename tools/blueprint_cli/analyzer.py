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
    analysis_file = os.path.join(analysis_dir, "analysis_result.json")

    # === AUTO-RESUME SUPPORT
    if os.path.exists(analysis_file):
        logger.info(f"🟡 Resuming from existing analysis: {analysis_file}")
        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            if "needs_splitting" in result:
                return result
            else:
                logger.warning("⚠️ Analysis result missing required field, re-running analysis...")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load existing analysis result: {e}")

    logger.info("🔍 Running analysis recipe")

    # Set up context for the recipe
    context = {"input": config.project_spec, "output_root": analysis_dir, "model": config.model}

    # Format guidance files for recipe
    guidance_files_str = format_files_for_recipe(config.guidance_files)
    # Add guidance files to context
    if guidance_files_str:
        context["guidance_files"] = guidance_files_str

    # Format context files for recipe
    context_files_str = format_files_for_recipe(config.context_files)
    # Add context files if available
    if context_files_str:
        context["context_files"] = context_files_str

    # Format reference docs for recipe
    reference_docs_str = format_files_for_recipe(config.reference_docs)
    # Add reference docs if available
    if reference_docs_str:
        context["reference_docs"] = reference_docs_str

    recipe_path = None
    # Check if component spec is provided
    if config.component_spec:
        # Ensure component spec is valid
        if not os.path.exists(config.component_spec):
            logger.error(f"Component spec file not found: {config.component_spec}")
            raise Exception(f"Component spec file not found: {config.component_spec}")

        # Add component spec to context
        context["component_spec"] = config.component_spec

        recipe_path = get_recipe_path("analyze_component.json")
    else:
        # Ensure project spec is valid
        if not os.path.exists(config.project_spec):
            logger.error(f"Project spec file not found: {config.project_spec}")
            raise Exception(f"Project spec file not found: {config.project_spec}")

        # Add project spec to context
        context["project_spec"] = config.project_spec

        recipe_path = get_recipe_path("analyze_project.json")

    # Run the recipe
    logger.info(f"Running project analysis with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error("Project analysis failed")
        raise Exception("Project analysis failed")

    # Check for analysis result file
    analysis_file = os.path.join(analysis_dir, "analysis_result.json")
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
