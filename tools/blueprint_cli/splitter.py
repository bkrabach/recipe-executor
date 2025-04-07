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
from utils import ensure_directory, format_files_for_recipe, load_file_content, pause_for_user, write_file_content

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
    components_dir = os.path.join(config.output_dir, "components")
    ensure_directory(components_dir)

    # === AUTO-RESUME: Load manifest if it already exists
    manifest_path = os.path.join(components_dir, "components_manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                existing_manifest = json.load(f)
            logger.info(f"Resuming from existing manifest: {manifest_path}")
            return existing_manifest
        except Exception as e:
            logger.warning(f"Failed to load existing manifest: {e}")

    if not analysis_result.get("needs_splitting", False):
        logger.info("Project doesn't need splitting, returning as a single component")

        # Reuse if spec file already exists
        component_id = "main_component"
        spec_filename = f"{component_id}_spec.md"
        spec_path = os.path.join(components_dir, spec_filename)

        if not os.path.exists(spec_path):
            logger.info("Generating single-component spec file...")
            spec_filename = generate_component_spec(config, components_dir, analysis_result)
        else:
            logger.info("Spec file already exists for main component, reusing...")

        component = {
            "component_id": component_id,
            "component_name": "Main Component",
            "description": "Single component implementation",
            "spec_file": spec_filename,
            "dependencies": [],
        }

        write_components_manifest([component], components_dir)
        pause_for_user(config)
        return [component]

    # === AUTO-RESUME: If already split, return manifest
    if os.path.exists(manifest_path):
        logger.info("Using cached components manifest")
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Otherwise run the full split
    logger.info("Splitting project into components...")
    component_specs = split_project(config)
    pause_for_user(config)

    final_components = []

    for component in component_specs:
        component_id = component["component_id"]
        component_spec_path = os.path.join(components_dir, component["spec_file"])
        sub_output_dir = os.path.join(components_dir, component_id)

        component_config = ProjectConfig(
            project_spec=config.project_spec,
            component_spec=component_spec_path,
            output_dir=sub_output_dir,
            target_project=config.target_project,
            model=config.model,
            verbose=config.verbose,
            auto_run=config.auto_run,
            context_files=config.context_files,
            reference_docs=config.reference_docs,
        )

        ensure_directory(component_config.output_dir)

        # === AUTO-RESUME: Skip component if final spec already analyzed
        analysis_result_path = os.path.join(component_config.output_dir, "analysis", "analysis_result.json")
        if os.path.exists(analysis_result_path):
            try:
                with open(analysis_result_path, "r", encoding="utf-8") as f:
                    component_analysis = json.load(f)
                logger.info(f"Resuming component analysis for {component_id}")
            except Exception:
                logger.warning(f"Could not load existing analysis for {component_id}, reanalyzing...")
                component_analysis = analyze_project(component_config)
        else:
            component_analysis = analyze_project(component_config)
            pause_for_user(config)

        if component_analysis.get("needs_splitting", False):
            logger.info(f"Component {component_id} needs further splitting")
            sub_components = split_project_recursively(component_config, component_analysis)
            final_components.extend(sub_components)
        else:
            final_components.append(component)

    return final_components


def split_project(config: ProjectConfig) -> List[Dict[str, Any]]:
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
    components_dir = os.path.join(config.output_dir, "components")
    ensure_directory(components_dir)

    manifest_file = os.path.join(components_dir, "components_manifest.json")

    # === AUTO-RESUME BLOCK ===
    if os.path.exists(manifest_file):
        logger.info(f"🔁 Resuming from manifest: {manifest_file}")
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # Check that all component spec files exist
            all_present = True
            for comp in manifest:
                spec_path = os.path.join(components_dir, comp.get("spec_file", ""))
                if not os.path.exists(spec_path):
                    logger.warning(f"Missing component spec file: {spec_path}")
                    all_present = False
                    break

            if all_present:
                logger.info("✅ All component specs present, skipping split.")
                return manifest
            else:
                logger.warning("⚠️ Some component specs are missing — re-running split.")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load or validate manifest: {e}")
            logger.info("Re-running split from scratch.")

    # Create output directories
    components_dir = os.path.join(config.output_dir, "components")
    ensure_directory(components_dir)

    # Set up context for the recipe
    context = {
        "input": config.project_spec if config.component_spec is None else config.component_spec,
        "analysis_result": os.path.join(config.output_dir, "analysis", "analysis_result.json"),
        "output_root": components_dir,
        "model": config.model,
    }

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
