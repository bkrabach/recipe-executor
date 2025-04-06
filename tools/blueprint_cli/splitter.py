"""
Project splitter module for the Blueprint CLI tool.

This module provides functions for splitting project specifications
into separate component specifications and recursively analyzing them.
"""

import json
import logging
import os
from typing import Any, Dict, List

from analyzer import analyze_project

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory, format_files_for_recipe, load_file_content, write_file_content

logger = logging.getLogger(__name__)


def split_project_recursively(config: ProjectConfig, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split a project recursively until all components are appropriately sized.

    Args:
        config: Project configuration
        analysis_result: Result from project analysis

    Returns:
        List of component specifications that don't need further splitting

    Raises:
        Exception: If splitting fails
    """
    # Create output directories
    components_dir = os.path.join(config.output_dir, "components")
    ensure_directory(components_dir)

    if not analysis_result.get("needs_splitting", False):
        logger.info("Project doesn't need splitting, returning as a single component")
        # Create a component spec for the project
        component = {
            "component_id": "main_component",
            "component_name": "Main Component",
            "description": "Single component implementation",
            "spec_file": generate_component_spec(config, components_dir, analysis_result),
            "dependencies": [],
        }
        write_components_manifest([component], components_dir)
        return [component]

    # Generate mini-specs for each component
    logger.info(f"Splitting project into {len(analysis_result['recommended_components'])} components")
    component_specs = split_project(config, analysis_result)

    # Create a list to hold all final leaf components (ones that don't need splitting)
    final_components = []

    # Recursively analyze each component
    for component in component_specs:
        component_id = component["component_id"]
        spec_path = os.path.join(components_dir, component["spec_file"])

        logger.info(f"Recursively analyzing component: {component_id}")

        # Create a new config for this component
        component_config = ProjectConfig(
            project_spec=spec_path,
            output_dir=os.path.join(config.output_dir, "components", component_id),
            target_project=config.target_project,
            model=config.model,
            verbose=config.verbose,
        )

        # Create the component output directory
        ensure_directory(component_config.output_dir)

        # Analyze the component
        try:
            component_analysis = analyze_project(component_config)

            if component_analysis.get("needs_splitting", False):
                logger.info(f"Component {component_id} needs further splitting")
                # Recursively split this component
                sub_components = split_project_recursively(component_config, component_analysis)
                final_components.extend(sub_components)
            else:
                logger.info(f"Component {component_id} is appropriately sized")
                # Add this component to the final list
                final_components.append(component)
        except Exception as e:
            logger.error(f"Failed to analyze component {component_id}: {e}")
            # Still include this component in the final list to avoid losing work
            final_components.append(component)

    return final_components


def split_project(config: ProjectConfig, analysis_result: Dict) -> List[Dict[str, Any]]:
    """
    Split a project into components based on analysis result.

    Args:
        config: Project configuration
        analysis_result: Result from project analysis

    Returns:
        List of component specifications

    Raises:
        Exception: If splitting fails
    """
    # Create output directories
    components_dir = os.path.join(config.output_dir, "components")
    ensure_directory(components_dir)

    # Format context files for recipe
    context_files_str = format_files_for_recipe(config.context_files)

    # Set up context for the recipe
    context = {
        "input": config.project_spec,
        "analysis_result": os.path.join(config.output_dir, "analysis", "project_analysis_result.json"),
        "output_root": components_dir,
        "model": config.model,
    }

    # Add context files if available
    if context_files_str:
        context["files"] = context_files_str

    # Get recipe path
    recipe_path = get_recipe_path("split_project.json")

    # Run the recipe
    logger.info(f"Running project splitting with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error("Project splitting failed")
        raise Exception("Project splitting failed")

    # Check for components manifest file
    manifest_file = os.path.join(components_dir, "components_manifest.json")
    if not os.path.exists(manifest_file):
        logger.error(f"Components manifest file not found: {manifest_file}")
        raise Exception("Components manifest file not found")

    # Load components manifest
    try:
        with open(manifest_file, "r") as f:
            components = json.load(f)

        logger.info(f"Generated {len(components)} component specifications")
        return components
    except Exception as e:
        logger.error(f"Failed to load components manifest: {e}")
        raise Exception(f"Failed to load components manifest: {e}")


def generate_component_spec(config: ProjectConfig, output_dir: str, analysis_result: Dict) -> str:
    """
    Generate a component specification for a project that doesn't need splitting.

    Args:
        config: Project configuration
        output_dir: Output directory for the component spec
        analysis_result: Analysis result for the project

    Returns:
        Path to the generated component spec file
    """
    # Create the component spec from the project spec
    component_id = "main_component"
    spec_filename = f"{component_id}_spec.md"

    # Load the project spec content
    project_spec_content = load_file_content(config.project_spec)

    # Create a simple component spec
    spec_content = f"""# Main Component Specification

## Overview
This component represents the entire project as it doesn't need further splitting.

{project_spec_content}
"""

    # Write the component spec
    spec_path = os.path.join(output_dir, spec_filename)
    write_file_content(spec_path, spec_content)

    return spec_filename


def write_components_manifest(components: List[Dict[str, Any]], output_dir: str) -> None:
    """
    Write the components manifest file.

    Args:
        components: List of component specifications
        output_dir: Output directory for the manifest
    """
    manifest_path = os.path.join(output_dir, "components_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(components, f, indent=2)

    logger.info(f"Wrote components manifest to {manifest_path}")
