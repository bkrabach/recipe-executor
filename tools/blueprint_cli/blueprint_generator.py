"""
Blueprint generator module for the Blueprint CLI tool.

This module provides functions for generating detailed implementation
blueprints from component specifications, including documentation
and implementation recipes.
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory

logger = logging.getLogger(__name__)


def generate_blueprint(
    component_id: str,
    spec_path: str,
    config: ProjectConfig,
    output_dir: str,
    dependency_info: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Generate a complete implementation blueprint for a component.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification file
        config: Project configuration
        output_dir: Output directory for generated files
        dependency_info: Optional dictionary of component dependencies

    Returns:
        Dict with generation results (paths to blueprint files)

    Raises:
        Exception: If generation fails
    """
    logger.info(f"Generating blueprint for component: {component_id}")

    # Create blueprint directory structure
    blueprint_dir = os.path.join(output_dir, "blueprints", config.target_project)
    component_dir = os.path.join(blueprint_dir, "components", component_id)
    reports_dir = os.path.join(blueprint_dir, "reports")

    ensure_directory(component_dir)
    ensure_directory(reports_dir)

    # Format context files for recipe
    context_files = []
    if config.context_files:
        context_files = [item["path"] for item in config.context_files]
    context_files_str = ",".join(context_files)

    # Extract dependencies if not provided
    if dependency_info is None:
        dependencies = extract_dependencies(component_id, spec_path)
        related_docs = []
    else:
        dependencies = dependency_info.get(component_id, [])
        # Look for documentation files for dependencies
        related_docs = []
        for dep_id in dependencies:
            dep_docs_path = os.path.join(blueprint_dir, "components", dep_id, f"{dep_id}_docs.md")
            if os.path.exists(dep_docs_path):
                related_docs.append(dep_docs_path)

    # Setup context for the recipe
    context = {
        "candidate_spec_path": spec_path,
        "component_id": component_id,
        "component_name": component_id.replace("_", " ").title(),
        "target_project": config.target_project,
        "output_root": output_dir,
        "model": config.model,
        "files": context_files_str,
    }

    # Add dependencies and related docs if available
    if dependencies:
        context["key_dependencies"] = ",".join(dependencies)

    if related_docs:
        context["related_docs"] = ",".join(related_docs)

    # Get recipe path
    recipe_path = get_recipe_path("build_blueprint.json")

    # Run the recipe
    logger.info(f"Running blueprint generation with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error(f"Failed to generate blueprint for {component_id}")
        raise Exception(f"Blueprint generation failed for component {component_id}")

    # Check for generated blueprint files
    spec_file = os.path.join(component_dir, f"{component_id}_spec.md")
    docs_file = os.path.join(component_dir, f"{component_id}_docs.md")
    create_recipe = os.path.join(component_dir, f"{component_id}_create.json")
    edit_recipe = os.path.join(component_dir, f"{component_id}_edit.json")
    summary_file = os.path.join(reports_dir, f"{component_id}_blueprint_summary.md")

    required_files = [spec_file, docs_file, create_recipe, edit_recipe]
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        logger.error(f"Missing blueprint files for {component_id}: {missing_files}")
        raise Exception(f"Blueprint generation incomplete for component {component_id}")

    logger.info(f"Successfully generated blueprint for {component_id}")

    return {
        "component_id": component_id,
        "spec_file": spec_file,
        "docs_file": docs_file,
        "create_recipe": create_recipe,
        "edit_recipe": edit_recipe,
        "summary_file": summary_file if os.path.exists(summary_file) else None,
        "dependencies": dependencies,
    }


def extract_dependencies(component_id: str, spec_path: str) -> List[str]:
    """
    Extract component dependencies from a specification file.

    Args:
        component_id: ID of the component
        spec_path: Path to the component specification file

    Returns:
        List of component IDs that this component depends on
    """
    logger.debug(f"Extracting dependencies for component: {component_id}")

    # Load specification content
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read specification file for {component_id}: {e}")
        return []

    # Look for dependency sections
    dependency_sections = [
        "## Component Dependencies",
        "### Internal Components",
        "## Dependencies",
        "## Internal Dependencies",
    ]

    dependencies = []

    for section in dependency_sections:
        if section in content:
            # Find the section content
            start_idx = content.find(section) + len(section)
            next_section_idx = content.find("##", start_idx)
            if next_section_idx == -1:
                section_content = content[start_idx:]
            else:
                section_content = content[start_idx:next_section_idx]

            # Look for component IDs in the section
            # Pattern for component IDs: likely snake_case words
            patterns = [
                r"\*\*([a-z][a-z0-9_]+)\*\*",  # Bold text: **component_id**
                r"- ([a-z][a-z0-9_]+)[^a-z0-9_]",  # List item: - component_id
                r"\b([a-z][a-z0-9_]+_component)\b",  # Words ending with _component
                r"\b([a-z][a-z0-9_]+_service)\b",  # Words ending with _service
                r"\b([a-z][a-z0-9_]+_manager)\b",  # Words ending with _manager
                r"\b([a-z][a-z0-9_]+_handler)\b",  # Words ending with _handler
            ]

            for pattern in patterns:
                matches = re.findall(pattern, section_content)
                for match in matches:
                    # Exclude common words that may match the pattern
                    if match and "_" in match and match != component_id:
                        dependencies.append(match)

    # Remove duplicates while preserving order
    seen = set()
    unique_dependencies = [dep for dep in dependencies if not (dep in seen or seen.add(dep))]

    logger.debug(f"Found dependencies for {component_id}: {unique_dependencies}")
    return unique_dependencies


def analyze_dependency_graph(
    components: List[Dict[str, str]],
    blueprint_dir: str,
) -> Dict[str, List[str]]:
    """
    Analyze dependencies between components to create a dependency graph.

    Args:
        components: List of component info dictionaries
        blueprint_dir: Directory containing blueprint files

    Returns:
        Dict mapping component_id to list of dependencies
    """
    logger.info(f"Analyzing dependency graph for {len(components)} components")

    dependency_graph = {}

    for component in components:
        component_id = component["component_id"]
        spec_path = component.get("spec_file")

        if not spec_path or not os.path.exists(spec_path):
            # Try to find the spec file in the blueprint directory
            spec_path = os.path.join(blueprint_dir, "components", component_id, f"{component_id}_spec.md")
            if not os.path.exists(spec_path):
                logger.warning(f"Specification file not found for component {component_id}")
                dependency_graph[component_id] = []
                continue

        # Extract dependencies
        dependencies = extract_dependencies(component_id, spec_path)
        dependency_graph[component_id] = dependencies

    # Validate dependencies (make sure all referenced components exist)
    all_components = {comp["component_id"] for comp in components}
    for component_id, deps in dependency_graph.items():
        unknown_deps = [dep for dep in deps if dep not in all_components]
        if unknown_deps:
            logger.warning(f"Component {component_id} has unknown dependencies: {unknown_deps}")
            # Remove unknown dependencies
            dependency_graph[component_id] = [dep for dep in deps if dep in all_components]

    return dependency_graph


def determine_generation_order(dependency_graph: Dict[str, List[str]]) -> List[str]:
    """
    Determine the order in which components should be generated based on dependencies.

    Args:
        dependency_graph: Dict mapping component_id to list of dependencies

    Returns:
        List of component_ids in generation order (dependencies first)
    """
    logger.info("Determining component generation order")

    # Topological sort to order components by dependencies
    visited = set()
    temp_visited = set()
    order = []

    def visit(component_id):
        if component_id in temp_visited:
            # Circular dependency detected
            logger.warning(f"Circular dependency detected involving component {component_id}")
            return

        if component_id in visited:
            return

        temp_visited.add(component_id)

        # Visit dependencies first
        for dep in dependency_graph.get(component_id, []):
            visit(dep)

        temp_visited.remove(component_id)
        visited.add(component_id)
        order.append(component_id)

    # Visit all components
    for component_id in dependency_graph:
        if component_id not in visited:
            visit(component_id)

    # Reverse the order so that dependencies come first
    generation_order = list(reversed(order))

    logger.info(f"Generation order determined: {', '.join(generation_order)}")
    return generation_order


def batch_generate_blueprints(
    components: List[Dict[str, str]],
    config: ProjectConfig,
    output_dir: str,
) -> Dict[str, Dict[str, str]]:
    """
    Generate blueprints for multiple components.

    Args:
        components: List of component info dictionaries
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Dict mapping component_id to blueprint generation results

    Raises:
        Exception: If generation fails
    """
    logger.info(f"Batch generating blueprints for {len(components)} components")

    # First analyze dependencies to optimize generation
    dependency_graph = {}
    for component in components:
        component_id = component["component_id"]
        spec_path = component.get("original_spec", component.get("revised_spec", component.get("spec_file")))

        if spec_path and os.path.exists(spec_path):
            dependency_graph[component_id] = extract_dependencies(component_id, spec_path)
        else:
            logger.warning(f"No spec file found for component {component_id}")
            dependency_graph[component_id] = []

    # Determine generation order
    generation_order = determine_generation_order(dependency_graph)

    # Generate blueprints in the determined order
    blueprint_results = {}

    for component_id in generation_order:
        component = next((c for c in components if c["component_id"] == component_id), None)
        if not component:
            logger.warning(f"Component info not found for {component_id}")
            continue

        spec_path = component.get("original_spec", component.get("revised_spec", component.get("spec_file")))
        if not spec_path or not os.path.exists(spec_path):
            logger.warning(f"No spec file found for component {component_id}")
            continue

        try:
            result = generate_blueprint(component_id, spec_path, config, output_dir, dependency_info=dependency_graph)
            blueprint_results[component_id] = result
        except Exception as e:
            logger.error(f"Failed to generate blueprint for component {component_id}: {e}")
            blueprint_results[component_id] = {
                "component_id": component_id,
                "status": "error",
                "error": str(e),
            }

    return blueprint_results
