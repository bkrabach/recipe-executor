=== File: tools/blueprint_cli/README.md ===
# Blueprint CLI

A modular tool for generating code from high-level specifications using AI-assisted generation with clean separation of concerns.

## Overview

Blueprint CLI takes a high-level project specification and analyzes it to determine if it should be split into smaller components. If splitting is needed, it creates detailed specifications for each component. The tool can then generate code for each component based on these specifications.

## Features

- **Clean Modular Design**: Clear separation of concerns with focused modules
- **Consistent File Handling**: Standardized approach to project specs, context files, and reference docs
- **Recursive Project Splitting**: Automatically breaks down large projects into appropriately sized components
- **Detailed Analysis**: Provides insights into project structure before code generation
- **AI-Assisted Generation**: Leverages LLMs to generate detailed specifications and code

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python -m blueprint_cli.cli --project-spec path/to/project_spec.md --output-dir output
```

### Advanced Usage

```bash
python -m blueprint_cli.cli \
  --project-spec path/to/project_spec.md \
  --context-files path/to/context1.md:rationale1,path/to/context2.md:rationale2 \
  --reference-docs path/to/ref1.md:rationale1,path/to/ref2.md:rationale2 \
  --output-dir output \
  --target-project my_project \
  --model openai:o3-mini \
  --verbose
```

### Command Line Arguments

- `--project-spec`: Path to the project specification file (required)
- `--context-files`: Comma-separated list of context files with optional rationales
- `--reference-docs`: Comma-separated list of reference docs with optional rationales
- `--output-dir`: Output directory (default: "output")
- `--target-project`: Target project name (default: "generated_project")
- `--model`: LLM model to use (default: "openai:o3-mini")
- `--verbose`: Enable verbose output

## Project Spec Format

The project specification is a markdown file that describes the project at a high level. It should include:

- Project overview and purpose
- Key requirements and functionality
- Architecture and design considerations
- Technical constraints and dependencies
- Implementation guidelines

## File Collections

The tool supports two types of file collections:

- **Context Files**: Global context that remains consistent throughout the pipeline
- **Reference Docs**: Component-specific documentation that varies by stage

Each file can include an optional rationale:

```
path/to/file.md:This file provides context about the project domain
```

## Output Structure

```
output/
├── analysis/
│   ├── project_analysis_result.json
│   └── project_analysis_summary.md
└── components/
    ├── components_manifest.json
    ├── component_1_spec.md
    ├── component_2_spec.md
    └── ...
```

## Development

### Project Structure

```
blueprint_cli/
├── __init__.py              # Package initialization with version
├── cli.py                   # CLI entry point and argument parsing
├── config.py                # Configuration handling
├── analyzer.py              # Project analysis logic
├── splitter.py              # Project splitting logic
├── executor.py              # Recipe execution wrapper
├── utils.py                 # Utility functions
├── ai_context/              # Built-in context files
│   ├── IMPLEMENTATION_PHILOSOPHY.md
│   └── MODULAR_DESIGN_PHILOSOPHY.md
└── recipes/                 # Recipe JSON files
    ├── analyze_project.json # Analyze project spec
    └── split_project.json   # Split project into components
```

### Extending the Tool

To extend the tool with new functionality:

1. Add new modules to the `blueprint_cli` package
2. Create new recipe files in the `recipes` directory
3. Update the CLI interface to expose the new functionality


=== File: tools/blueprint_cli/TOOL_DEVELOPMENT_STATUS.md ===
# Blueprint CLI: Development Status and Guidance Document

## Project Overview

Blueprint CLI is a modular tool designed to generate code from high-level specifications using AI-assisted generation. The tool follows these core principles:

1. **Clean Modular Design**: Clear separation of concerns with focused modules
2. **Location-Agnostic**: Works regardless of where it's installed or run from
3. **Recursive Analysis**: Can analyze complex projects and break them down into appropriately sized components
4. **Consistent File Handling**: Standardized approach for file references

The tool is built to work with the existing recipe_executor system, allowing it to leverage AI models to analyze project specifications, determine appropriate component splitting, and eventually generate code.

## Current Implementation

### Core Features Implemented

1. **Project Analysis**: Analyzes a project specification to determine if it should be split into smaller components
2. **Recursive Component Splitting**: Recursively splits projects until all components are appropriately sized
3. **File Reference Resolution**: Flexibly resolves file paths mentioned in project specifications
4. **Configuration Management**: Loads and manages configuration from files and command-line arguments

### Directory Structure

```
blueprint_cli/
├── __init__.py               # Package initialization with version
├── analyzer.py              # Project analysis logic
├── cli.py                   # CLI entry point and argument parsing
├── config.py                # Configuration handling
├── executor.py              # Recipe execution wrapper
├── splitter.py              # Project splitting logic (recursive)
├── utils.py                 # Utility functions
├── ai_context/              # Built-in context files
│   ├── IMPLEMENTATION_PHILOSOPHY.md
│   └── MODULAR_DESIGN_PHILOSOPHY.md
└── recipes/                 # Recipe JSON files
    ├── analyze_project.json # Analyze project spec
    └── split_project.json   # Split project into components
```

### Command-Line Interface

The tool currently supports these arguments:

```
--project-spec       Path to the project specification file (required)
--output-dir         Output directory for generated files (default: "output")
--target-project     Name of the target project (default: "generated_project")
--model              LLM model to use (default: "openai:o3-mini")
--verbose            Enable verbose output
--max-recursion-depth  Maximum recursion depth for component splitting (default: 3)
```

### Current Workflow

1. The user creates a project specification in Markdown with a "File References" section
2. The tool analyzes the project to determine if it needs to be split into components
3. If splitting is needed, it creates individual component specifications
4. Each component is recursively analyzed to see if it needs further splitting
5. This continues until all components are appropriately sized or max depth is reached
6. A summary of final components is generated

## Next Steps & Development Roadmap

### Immediate Next Tasks

1. **Component Processing Pipeline**:

   - Implement the clarification questions/answers workflow for individual components
   - Add component evaluation to determine if components need human review
   - Implement human review integration

2. **Blueprint Generation**:

   - Create detailed blueprints for each component that passes evaluation
   - Include all necessary files for implementation (specs, documentation, etc.)

3. **Code Generation**:
   - Implement code generation from blueprints
   - Handle component dependencies during code generation
   - Generate code for all components in the right order based on dependencies

### Planned Improvements

1. **Error Handling**:

   - Improve error detection and reporting
   - Add fallback strategies for common errors

2. **Dependency Management**:

   - Enhance detection of dependencies between components
   - Implement dependency graph for optimal component processing order
   - Validate component interfaces against dependencies

3. **Test Suite**:
   - Create unit tests for core functionality
   - Add integration tests for the entire pipeline

## Development Guidelines

### Recipe Patterns

When creating new recipe JSON files, follow these patterns:

1. Always specify explicit filenames in write_files steps
2. Use {{input}}, {{output_root}}, and {{model}} consistently
3. Handle optional files with appropriate merge modes
4. Structure prompts with clear sections for Project Specification, Analysis Result, etc.

### Code Guidelines

1. Follow the Implementation Philosophy document for coding style
2. Keep functions focused on a single responsibility
3. Prioritize ruthless simplicity over clever abstractions
4. Use comprehensive logging for debugging
5. Make path resolution flexible and robust

### Testing the Tool

To test the current implementation:

```bash
python tools/blueprint_cli/cli.py \
  --project-spec tools/blueprint_cli/sample/sample_project_spec.md \
  --output-dir output \
  --max-recursion-depth 3 \
  --verbose
```

This will analyze the sample project, split it into components, and recursively analyze each component.

## Architecture Notes

### Key Design Patterns

1. **Recipe-driven workflow**: The tool uses recipe JSON files to define the steps for analysis, splitting, etc.
2. **Config-based initialization**: Configuration is loaded from the project spec and command-line arguments
3. **Path-agnostic file resolution**: Files are resolved relative to various base directories
4. **Recursive processing**: The tool can analyze and split projects recursively

### Integration Points

1. **Recipe Executor**: The tool relies on recipe_executor for running AI-powered transformations
2. **AI Models**: By default, the tool uses openai:o3-mini but can be configured to use other models
3. **File System**: The tool reads/writes files in a structured way across directories

## Conclusion

The Blueprint CLI tool is making good progress with a solid foundation for project analysis and recursive component splitting. The next major features to implement are the component processing pipeline, blueprint generation, and code generation. Focus on maintaining the tool's modular design and ruthless simplicity while adding these new capabilities.


=== File: tools/blueprint_cli/__init__.py ===
"""
Blueprint CLI - A modular tool for generating code from specifications
using AI-assisted generation with clean separation of concerns.
"""

__version__ = "0.1.0"


=== File: tools/blueprint_cli/analyzer.py ===
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


=== File: tools/blueprint_cli/answer_processor.py ===
"""
Answer processor module for the Blueprint CLI tool.

This module handles generating answers to clarification questions and
producing revised component specifications.
"""

import logging
import os
from typing import Dict

# Local imports
from config import ProjectConfig
from executor import get_recipe_path, run_recipe
from utils import ensure_directory

logger = logging.getLogger(__name__)


def generate_answers(
    component_id: str,
    spec_path: str,
    questions_path: str,
    config: ProjectConfig,
    output_dir: str,
) -> str:
    """
    Generate answers to clarification questions and a revised component specification.

    Args:
        component_id: ID of the component
        spec_path: Path to the original component specification file
        questions_path: Path to the clarification questions file
        config: Project configuration
        output_dir: Output directory for generated files

    Returns:
        Path to the revised specification file

    Raises:
        Exception: If answer generation fails
    """
    logger.info(f"Generating clarification answers for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define the expected output file path
    revised_spec_path = os.path.join(output_dir, f"{component_id}_candidate_spec_revised.md")

    # Check if output already exists (for resuming)
    if os.path.exists(revised_spec_path):
        logger.info(f"Revised specification already exists for {component_id}")
        return revised_spec_path

    # Format context files for recipe
    context_files = []
    if config.context_files:
        context_files = [item["path"] for item in config.context_files]
    context_files_str = ",".join(context_files)

    # Set up context for the recipe
    context = {
        "candidate_spec_path": spec_path,
        "clarification_questions_path": questions_path,
        "component_id": component_id,
        "output_root": output_dir,
        "model": config.model,
    }

    # Add context files if available
    if context_files_str:
        context["context_files"] = context_files_str

    # Get recipe path
    recipe_path = get_recipe_path("generate_clarification_answers.json")

    # Run the recipe
    logger.info(f"Running answer generation with recipe: {recipe_path}")
    success = run_recipe(recipe_path, context, config.verbose)

    if not success:
        logger.error(f"Failed to generate clarification answers for {component_id}")
        raise Exception(f"Answer generation failed for component {component_id}")

    # Check for revised specification file
    if not os.path.exists(revised_spec_path):
        logger.error(f"Revised specification file not found: {revised_spec_path}")
        raise Exception(f"Revised specification not found for component {component_id}")

    logger.info(f"Successfully generated revised specification for {component_id}")
    return revised_spec_path


def generate_answers_from_template(
    component_id: str, spec_path: str, questions_path: str, answers: Dict[str, str], output_dir: str = "output"
) -> str:
    """
    Generate a revised specification based on provided answers.

    This is a simpler alternative to using the recipe-based generation
    when testing or when the recipe executor is not available.

    Args:
        component_id: ID of the component
        spec_path: Path to the original component specification
        questions_path: Path to the clarification questions
        answers: Dictionary of question/answer pairs
        output_dir: Output directory for generated files

    Returns:
        Path to the revised specification file
    """
    logger.info(f"Generating revised specification with manual answers for component: {component_id}")

    # Ensure output directory exists
    ensure_directory(output_dir)

    # Define the expected output file path
    revised_spec_path = os.path.join(output_dir, f"{component_id}_candidate_spec_revised.md")

    # Check if output already exists
    if os.path.exists(revised_spec_path):
        logger.info(f"Revised specification already exists for {component_id}")
        return revised_spec_path

    # Read the original spec
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            original_spec = f.read()
    except Exception as e:
        logger.error(f"Failed to read original specification: {e}")
        raise Exception(f"Failed to read original specification for component {component_id}")

    # Generate a revised spec with the answers
    answers_section = "## Clarification Answers\n\n"
    for question, answer in answers.items():
        answers_section += f"**Q: {question}**\n\n{answer}\n\n"

    revised_spec = f"{original_spec}\n\n{answers_section}"

    # Write the revised spec
    try:
        with open(revised_spec_path, "w", encoding="utf-8") as f:
            f.write(revised_spec)
        logger.info(f"Generated revised specification at {revised_spec_path}")
        return revised_spec_path
    except Exception as e:
        logger.error(f"Failed to write revised specification: {e}")
        raise Exception(f"Failed to write revised specification for component {component_id}")


=== File: tools/blueprint_cli/blueprint_generator.py ===
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


=== File: tools/blueprint_cli/cli.py ===
#!/usr/bin/env python3
"""
Command-line interface for the Blueprint CLI tool.

This module handles argument parsing and dispatches commands
to the appropriate modules.
"""

import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Import local modules using relative paths based on script location
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Local imports
from analyzer import analyze_project  # noqa: E402
from config import ProjectConfig, create_config_from_args  # noqa: E402
from splitter import split_project_recursively  # noqa: E402
from utils import ensure_directory, pause_for_user, setup_logging  # noqa: E402

# Get version from package or default if not available
try:
    from __init__ import __version__
except ImportError:
    __version__ = "0.1.0"


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Blueprint CLI - Generate code from specifications using AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add version argument
    parser.add_argument("--version", action="version", version=f"Blueprint CLI v{__version__}")

    # Required arguments
    parser.add_argument("--project-spec", required=True, help="Path to the project specification file")

    # Output options
    parser.add_argument("--output-dir", default="output", help="Output directory for generated files")
    parser.add_argument("--target-project", default="generated_project", help="Name of the target project")

    # Processing options
    parser.add_argument("--model", default="openai:o3-mini", help="LLM model to use for generation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--auto-run", action="store_true", dest="auto_run", help="Automatically run all steps without pausing between"
    )
    parser.add_argument(
        "--max-recursion-depth", type=int, default=3, help="Maximum recursion depth for component splitting"
    )

    # Component processing options
    parser.add_argument("--skip-processing", action="store_true", help="Skip the component processing phase")
    parser.add_argument("--process-review", help="Process human review feedback for a component (provide component ID)")
    parser.add_argument("--review-path", help="Path to the updated spec from human review (used with --process-review)")
    parser.add_argument("--component-filter", help="Only process components matching this prefix")

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Blueprint CLI tool.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Parse arguments
    parsed_args = parse_args(args)

    # Setup logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Blueprint CLI v{__version__}")

    # Create configuration
    try:
        config = create_config_from_args(parsed_args)
        logger.debug(f"Configuration: {config}")

        if config.context_files:
            logger.info(f"Found {len(config.context_files)} context files in project spec")
        if config.reference_docs:
            logger.info(f"Found {len(config.reference_docs)} reference docs in project spec")
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        return 1

    # Handle processing human review feedback
    if parsed_args.process_review:
        component_id = parsed_args.process_review
        review_path = parsed_args.review_path

        if not review_path:
            logger.error("--review-path is required when using --process-review")
            return 1

        if not os.path.exists(review_path):
            logger.error(f"Review path not found: {review_path}")
            return 1

        logger.info(f"Processing human review feedback for component: {component_id}")

        # Import component_processor here to avoid circular imports
        from component_processor import process_human_review_feedback

        try:
            result = process_human_review_feedback(component_id, review_path, config, config.output_dir)

            logger.info(f"Feedback processing result: {result}")

            if result.get("needs_review", False):
                logger.info(f"Component {component_id} still needs review after processing feedback")
            else:
                logger.info(f"Component {component_id} is now ready after processing feedback")

            pause_for_user(config)

            return 0
        except Exception as e:
            logger.error(f"Failed to process human review feedback: {e}")
            return 1

    # Ensure project_spec exists
    if not os.path.exists(config.project_spec):
        logger.error(f"Project specification file not found: {config.project_spec}")
        return 1

    # Ensure output directory exists
    try:
        ensure_directory(config.output_dir)
        logger.debug(f"Output directory: {config.output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        return 1

    # Run the project analysis
    try:
        logger.info("Analyzing project specification...")
        result = analyze_project(config)

        pause_for_user(config)

        if result["needs_splitting"]:
            logger.info("Project needs to be split into components")

            # Set recursion limit based on CLI argument
            sys.setrecursionlimit(max(1000, parsed_args.max_recursion_depth * 2))

            # Recursively split the project
            final_components = split_project_recursively(config, result)

            logger.info(f"Loaded {len(final_components)} final components (resume-aware)")

            logger.info(f"Recursive splitting complete, produced {len(final_components)} final components")

            # Write a summary of the final components
            summary_path = os.path.join(config.output_dir, "final_components_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                import json

                json.dump(final_components, f, indent=2)

            logger.info(f"Final components summary written to {summary_path}")

            # Continue to component processing phase
            if not parsed_args.skip_processing:
                logger.info("Proceeding to component processing phase...")
                process_components(config, final_components)

        else:
            logger.info("Project is small enough to process as a single component")

            # Create a single component spec
            component_id = "main_component"
            spec_filename = f"{component_id}_spec.md"
            spec_path = os.path.join(config.output_dir, "components", spec_filename)

            # Process the single component if it exists
            if os.path.exists(spec_path) and not parsed_args.skip_processing:
                logger.info("Processing the single component...")
                single_component = [
                    {
                        "component_id": component_id,
                        "component_name": "Main Component",
                        "description": "Single component implementation",
                        "spec_file": spec_filename,
                        "dependencies": [],
                    }
                ]
                process_components(config, single_component)

        logger.info("Blueprint generation completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Blueprint generation failed: {e}")
        return 1


def process_components(config: ProjectConfig, components: List[Dict[str, Any]]) -> None:
    """
    Process component specifications through the clarification and evaluation workflow.

    Args:
        config: Project configuration
        components: List of component dictionaries from the splitting phase
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Processing {len(components)} components")

    # Check if we have existing evaluation files
    eval_dir = os.path.join(config.output_dir, "evaluation")
    if os.path.exists(eval_dir):
        eval_files = os.listdir(eval_dir)
        logger.info(f"Found {len(eval_files)} existing evaluation files: {eval_files}")

        # Extract component IDs from evaluation files
        processed_components = {}
        for filename in eval_files:
            if filename.endswith("_evaluation_summary.md"):
                component_id = filename.replace("_evaluation_summary.md", "")
                eval_path = os.path.join(eval_dir, filename)
                revised_spec_path = os.path.join(
                    config.output_dir, "clarification", f"{component_id}_candidate_spec_revised.md"
                )

                if os.path.exists(revised_spec_path):
                    # Read evaluation to check if it needs review
                    with open(eval_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        needs_review = "NEEDS FURTHER REVIEW: Yes" in content

                    processed_components[component_id] = {"needs_review": needs_review, "spec_path": revised_spec_path}
                    logger.debug(f"Found processed component: {component_id}, needs_review: {needs_review}")

        if processed_components:
            logger.info(f"Found {len(processed_components)} previously processed components")

            # Check if all components in the current run have already been processed
            all_processed = True
            for component in components:
                component_id = component["component_id"]
                if component_id not in processed_components:
                    all_processed = False
                    logger.debug(f"Component {component_id} has not been processed yet")

            if all_processed:
                logger.info("All components already processed, skipping to blueprint generation")

                needs_review = [comp_id for comp_id, result in processed_components.items() if result["needs_review"]]
                completed = [comp_id for comp_id, result in processed_components.items() if not result["needs_review"]]

                logger.info(f"Found {len(completed)} components ready, {len(needs_review)} need review")

                # Import blueprint generator
                from blueprint_generator import batch_generate_blueprints

                # Generate blueprints for completed components
                if completed:
                    logger.info(f"Generating blueprints for {len(completed)} ready components...")
                    try:
                        # Create component info dictionaries for blueprint generation
                        complete_components = []
                        for component in components:
                            if component["component_id"] in completed:
                                component_id = component["component_id"]
                                complete_components.append({
                                    "component_id": component_id,
                                    "revised_spec": processed_components[component_id]["spec_path"],
                                    "spec_file": component.get("spec_file", f"{component_id}_spec.md"),
                                })

                        blueprint_results = batch_generate_blueprints(complete_components, config, config.output_dir)
                        logger.info(f"Successfully generated blueprints for {len(blueprint_results)} components")
                    except Exception as e:
                        logger.error(f"Blueprint generation failed: {e}")

                return

    # Import component_processor here to avoid circular imports
    from component_processor import batch_process_components

    # Convert components to the format expected by batch_process_components
    component_specs = []
    for component in components:
        component_id = component["component_id"]
        spec_file = component["spec_file"]
        spec_path = os.path.join(config.output_dir, "components", spec_file)

        if os.path.exists(spec_path):
            component_specs.append((component_id, spec_path))
        else:
            logger.warning(f"Component specification not found: {spec_path}")

    if not component_specs:
        logger.error("No component specifications found to process")
        return

    # Process the components
    try:
        results = batch_process_components(component_specs, config, config.output_dir)

        # Check results
        needs_review = []
        completed = []

        for component_id, result in results.items():
            if result.get("needs_review", False):
                needs_review.append(component_id)
            else:
                completed.append(component_id)

        # Print summary
        logger.info(
            f"Component processing complete. {len(completed)} components ready, {len(needs_review)} need review"
        )

        if needs_review:
            logger.info("Components needing human review:")
            for component_id in needs_review:
                logger.info(f"  - {component_id}")

            logger.info(f"Please review these components in the {config.output_dir}/human_review directory")
            logger.info("After review, you can run the CLI again with the --process-review flag")

        # Import blueprint generator
        from blueprint_generator import batch_generate_blueprints

        # Generate blueprints for completed components
        if completed:
            logger.info(f"Generating blueprints for {len(completed)} ready components...")
            try:
                blueprint_results = batch_generate_blueprints(
                    [c for c in components if c["component_id"] in completed], config, config.output_dir
                )
                logger.info(f"Successfully generated blueprints for {len(blueprint_results)} components")
            except Exception as e:
                logger.error(f"Blueprint generation failed: {e}")

    except Exception as e:
        logger.error(f"Component processing failed: {e}")


if __name__ == "__main__":
    sys.exit(main())


=== File: tools/blueprint_cli/component_evaluator.py ===
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


=== File: tools/blueprint_cli/component_processor.py ===
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


=== File: tools/blueprint_cli/component_processor_test.py ===
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


=== File: tools/blueprint_cli/config.py ===
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProjectConfig:
    """Configuration for a project."""

    project_spec: str
    component_spec: Optional[str] = None
    output_dir: str = "output"
    target_project: str = "generated_project"
    guidance_files: List[Dict[str, str]] = field(default_factory=list)
    context_files: List[Dict[str, str]] = field(default_factory=list)
    reference_docs: List[Dict[str, str]] = field(default_factory=list)
    model: str = "openai:o3-mini"
    verbose: bool = False
    auto_run: bool = False

    def __post_init__(self):
        self._add_guidance_files()
        # Only auto-extract if not provided explicitly
        if os.path.exists(self.project_spec) and not (self.context_files or self.reference_docs):
            self._extract_file_references_from_spec()

    def _add_guidance_files(self):
        """Add built-in guidance files to the guidance_files list."""
        module_dir = os.path.dirname(os.path.abspath(__file__))
        ai_context_dir = os.path.join(module_dir, "ai_context")
        guidance_files = [
            {
                "path": os.path.join(ai_context_dir, "IMPLEMENTATION_PHILOSOPHY.md"),
                "rationale": "Core implementation philosophy guide",
            },
            {
                "path": os.path.join(ai_context_dir, "MODULAR_DESIGN_PHILOSOPHY.md"),
                "rationale": "Modular design principles guide",
            },
        ]
        for file_info in guidance_files:
            if os.path.exists(file_info["path"]):
                if not any(item.get("path") == file_info["path"] for item in self.context_files):
                    self.guidance_files.append(file_info)

    def _extract_file_references_from_spec(self):
        """Parse the spec into sections and extract file references."""
        try:
            with open(self.project_spec, "r", encoding="utf-8") as f:
                content = f.read()
            sections = self._parse_sections(content)
            if "Context Files" in sections:
                self._parse_file_references(sections["Context Files"], self.context_files)
            else:
                print("Warning: No 'Context Files' section found in the project spec.")
            if "Reference Docs" in sections:
                self._parse_file_references(sections["Reference Docs"], self.reference_docs)
            else:
                print("Warning: No 'Reference Docs' section found in the project spec.")
        except Exception as e:
            print(f"Warning: Failed to extract file references from spec: {e}")

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parse the document into sections based on markdown headings.
        Returns a dictionary mapping heading text to the content until the next heading.
        Raises an error if the same heading appears more than once.
        """
        sections = {}
        current_heading: Optional[str] = None
        current_lines: List[str] = []
        for line in content.splitlines():
            heading_match = re.match(r"^\s*(#{1,6})\s*(.+?)\s*$", line)
            if heading_match:
                # Save the previous section, if any.
                if current_heading is not None:
                    if current_heading in sections:
                        raise ValueError(f"Multiple '{current_heading}' sections found in the project spec.")
                    sections[current_heading] = "\n".join(current_lines).strip()
                current_heading = heading_match.group(2)
                current_lines = []
            else:
                if current_heading is not None:
                    current_lines.append(line)
        if current_heading is not None:
            if current_heading in sections:
                raise ValueError(f"Multiple '{current_heading}' sections found in the project spec.")
            sections[current_heading] = "\n".join(current_lines).strip()
        return sections

    def _parse_file_references(self, section_content: str, target_list: List[Dict[str, str]]):
        """
        Parses file references from a section. Each nonempty line must be in the format:

          - `path/to/file`: Rationale for file

        The leading dash is optional.
        Throws an error if a line does not conform.
        """
        pattern = r"^\s*(-\s*)?`([^`]+)`:\s*(.+)$"
        for line in section_content.splitlines():
            line = line.strip()
            if not line:
                continue
            match = re.match(pattern, line)
            if not match:
                raise ValueError(
                    f"Invalid file reference format: '{line}'. Expected format: `path/to/file`: Rationale for file"
                )
            file_path = match.group(2).strip()
            rationale = match.group(3).strip()
            file_path = self._resolve_path(file_path)
            if os.path.exists(file_path):
                target_list.append({"path": file_path, "rationale": rationale})
            else:
                print(f"Warning: Referenced file not found: {file_path}")

    def _resolve_path(self, path: str) -> str:
        """
        Resolve a file path relative to multiple possible locations.
        """
        if os.path.isabs(path):
            return path
        cwd_path = os.path.abspath(path)
        if os.path.exists(cwd_path):
            return cwd_path
        spec_dir = os.path.dirname(os.path.abspath(self.project_spec))
        spec_relative_path = os.path.normpath(os.path.join(spec_dir, path))
        if os.path.exists(spec_relative_path):
            return spec_relative_path
        if "sample" in spec_dir:
            sample_dir = os.path.join(spec_dir.split("sample")[0], "sample")
            sample_docs_path = os.path.normpath(os.path.join(sample_dir, "docs", path))
            if os.path.exists(sample_docs_path):
                return sample_docs_path
            sample_relative_path = os.path.normpath(os.path.join(sample_dir, path))
            if os.path.exists(sample_relative_path):
                return sample_relative_path
        return spec_relative_path

    def get_context_paths(self) -> List[str]:
        return [item["path"] for item in self.context_files]

    def get_reference_paths(self) -> List[str]:
        return [item["path"] for item in self.reference_docs]


def create_config_from_args(args) -> ProjectConfig:
    return ProjectConfig(
        project_spec=args.project_spec,
        output_dir=args.output_dir,
        target_project=args.target_project,
        model=args.model,
        verbose=args.verbose,
    )


=== File: tools/blueprint_cli/executor.py ===
"""
Recipe executor module for the Blueprint CLI tool.

This module provides functions for executing recipes with the recipe_executor.
"""

import logging
import os
import subprocess
from typing import Dict

# Local imports
from utils import safe_print

logger = logging.getLogger(__name__)


def run_recipe(recipe_path: str, context: Dict[str, str], verbose: bool = False) -> bool:
    """
    Run a recipe with recipe_executor.

    Args:
        recipe_path: Path to the recipe file
        context: Context dictionary to pass to the recipe
        verbose: Whether to show verbose output

    Returns:
        True if the recipe executed successfully, False otherwise
    """
    # Find recipe_executor assuming we're running from parent directory
    # This allows flexibility in where blueprint_cli is located
    recipe_executor_path = "recipe_executor/main.py"

    # Verify path exists
    if not os.path.exists(recipe_executor_path):
        logger.warning(f"Recipe executor not found at {recipe_executor_path}. Trying relative path.")

        # Try a relative path from this script
        module_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(module_dir)
        alternate_path = os.path.join(parent_dir, "recipe_executor", "main.py")

        if os.path.exists(alternate_path):
            recipe_executor_path = alternate_path
        else:
            logger.error("Recipe executor not found. Make sure you're running from the parent directory.")
            return False

    # Construct command
    cmd = ["python", recipe_executor_path, recipe_path]

    # Add context parameters
    for key, value in context.items():
        cmd.extend(["--context", f"{key}={value}"])

    logger.debug(f"Running recipe: {' '.join(cmd)}")

    # Run command
    if verbose:
        # Show all output in real-time
        safe_print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        success = result.returncode == 0
    else:
        # Only show summary
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        if success:
            logger.info(f"Recipe completed successfully: {recipe_path}")
        else:
            logger.error(f"Error running recipe: {result.stderr}")

    return success


def get_recipe_path(recipe_name: str) -> str:
    """
    Get the full path to a recipe file.

    Args:
        recipe_name: Name of the recipe file

    Returns:
        Full path to the recipe file
    """
    # Get the directory of this module (works regardless of installation location)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    recipes_dir = os.path.join(module_dir, "recipes")

    # Ensure recipes directory exists
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir, exist_ok=True)

    return os.path.join(recipes_dir, recipe_name)


=== File: tools/blueprint_cli/question_generator.py ===
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


=== File: tools/blueprint_cli/recipes/analyze_component.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "project_spec",
      "optional": false
    },
    {
      "type": "read_files",
      "path": "{{component_spec}}",
      "artifact": "component_spec_content",
      "optional": false
    },
    {
      "type": "read_files",
      "path": "{{guidance_files}}",
      "artifact": "guidance_files_content",
      "optional": false,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{context_files}}",
      "artifact": "context_files_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{reference_docs}}",
      "artifact": "reference_docs_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "# Component Analysis Task\n\nYou are an expert software architect analyzing a component specification to determine if it should be split further into multiple sub-components according to our modular design guidance philosophy.\n\n## Component Specification\n\n<COMPONENT_SPEC>\n{{ component_spec_content }}\n</COMPONENT_SPEC>\n\nThe component is part of a larger project. The project overview is included only to provide context for what the component is a part of. The component and your analysis, however, does not need to be concerned with its place in the larger project, per our guidance philosophy docs.\n\n## Project Overview\n\n<PROJECT_OVERVIEW>\n{{project_spec}}\n</PROJECT_OVERVIEW>\n\n## Guidance Philosophy (how to make decisions)\n\n<GUIDANCE_FILES>\n{{guidance_files_content}}\n</GUIDANCE_FILES>{% if context_files %}\n\n## Context Files\n\n<CONTEXT_FILES>\n{{context_files_content}}\n</CONTEXT_FILES>{% endif %}{% if reference_docs_content %}\n\n## Reference Docs\n\n<REFERENCE_DOCS>\n{{reference_docs_content}}\n</REFERENCE_DOCS>{% endif %}\n\n## Your Task\n\nAnalyze the component specification and determine if it represents a component that is appropriately sized for implementation, or if it should be split into smaller sub-components, per our modular design guidance philosophy. ONLY CONSIDER THE COMPONENT SPEC - the project overview is only for understanding the surrounding context.\n\nIf the component needs to be split, briefly outline what the major sub-components should be, with a 1-2 sentence description for each.\n\n## Output Format\n\nProvide your analysis as a JSON object with the following structure:\n\n```json\n{\n  \"needs_splitting\": true/false,\n  \"reasoning\": \"Explanation of your decision\",\n  \"recommended_components\": [\n    {\n      \"component_id\": \"component_identifier\",\n      \"component_name\": \"Human Readable Component Name\",\n      \"description\": \"Brief description of this component\"\n    },\n  ]\n}\n```\n\nIf the component doesn't need splitting, the `recommended_components` array should be empty.\n\nComponent IDs should be in snake_case, lowercase, and descriptive of the component's purpose.\n\nFilename should be `analysis_result.json` with no directories or paths.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "analysis_result"
    },
    {
      "type": "write_files",
      "artifact": "analysis_result",
      "root": "{{output_root}}"
    },
    {
      "type": "generate",
      "prompt": "# Component Analysis Summary\n\nYou are an expert software architect creating a readable summary of a component analysis. You've analyzed a component specification and determined whether it should be split into multiple sub-components.\n\n## Component Specification\n\n<COMPONENT_SPEC>\n{{ component_spec_content }}\n</COMPONENT_SPEC>\n\n## Analysis Result\n\n<ANALYSIS_RESULT>\n{{analysis_result}}\n</ANALYSIS_RESULT>\n\n## Your Task\n\nCreate a human-readable markdown document that summarizes your analysis. The document should include:\n\n1. A brief overview of the component\n2. Your assessment of whether the component needs to be split and why\n3. If splitting is recommended, a description of each recommended sub-component\n4. Next steps based on your analysis\n\nMake your summary clear, concise, and actionable for the development team.\n\n## Output Format\n\nProvide your summary as a markdown document. The filename should be `analysis_summary.md` with no directories or paths.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "analysis_summary"
    },
    {
      "type": "write_files",
      "artifact": "analysis_summary",
      "root": "{{output_root}}"
    }
  ]
}


=== File: tools/blueprint_cli/recipes/analyze_project.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "project_spec",
      "optional": false
    },
    {
      "type": "read_files",
      "path": "{{guidance_files}}",
      "artifact": "guidance_files_content",
      "optional": false,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{context_files}}",
      "artifact": "context_files_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{reference_docs}}",
      "artifact": "reference_docs_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "# Project Analysis Task\n\nYou are an expert software architect analyzing a project to determine if it should be split into multiple components according to our modular design guidance philosophy.\n\n## Project Specification (overrides context files or reference docs where discrepancies)\n\n<PROJECT_SPEC>\n{{project_spec}}\n</PROJECT_SPEC>\n\n## Guidance Philosophy (how to make decisions)\n\n<GUIDANCE_FILES>\n{{guidance_files_content}}\n</GUIDANCE_FILES>{% if context_files %}\n\n## Context Files\n\n<CONTEXT_FILES>\n{{context_files_content}}\n</CONTEXT_FILES>{% endif %}{% if reference_docs_content %}\n\n## Reference Docs\n\n<REFERENCE_DOCS>\n{{reference_docs_content}}\n</REFERENCE_DOCS>{% endif %}\n\n## Your Task\n\nAnalyze the project specification and determine if it represents a component that is appropriately sized for implementation, or if it should be split into smaller components, per our modular design guidance philosophy.\n\nIf the project needs to be split, briefly outline what the major components should be, with a 1-2 sentence description for each.\n\n## Output Format\n\nProvide your analysis as a JSON object with the following structure:\n\n```json\n{\n  \"needs_splitting\": true/false,\n  \"reasoning\": \"Explanation of your decision\",\n  \"recommended_components\": [\n    {\n      \"component_id\": \"component_identifier\",\n      \"component_name\": \"Human Readable Component Name\",\n      \"description\": \"Brief description of this component\"\n    }\n  ]\n}\n```\n\nIf the project doesn't need splitting, the `recommended_components` array should be empty.\n\nComponent IDs should be in snake_case, lowercase, and descriptive of the component's purpose.\n\nFilename should be `analysis_result.json` with no directories or paths.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "analysis_result"
    },
    {
      "type": "write_files",
      "artifact": "analysis_result",
      "root": "{{output_root}}"
    },
    {
      "type": "generate",
      "prompt": "# Project Analysis Summary\n\nYou are an expert software architect creating a readable summary of a project analysis. You've analyzed a project specification and determined whether it should be split into multiple components.\n\n## Project Specification\n\n<PROJECT_SPEC>\n{{project_spec}}\n</PROJECT_SPEC>\n\n## Analysis Result\n\n<ANALYSIS_RESULT>\n{{analysis_result}}\n</ANALYSIS_RESULT>\n\n## Your Task\n\nCreate a human-readable markdown document that summarizes your analysis. The document should include:\n\n1. A brief overview of the project\n2. Your assessment of whether the project needs to be split and why\n3. If splitting is recommended, a description of each recommended component\n4. Next steps based on your analysis\n\nMake your summary clear, concise, and actionable for the project team.\n\n## Output Format\n\nProvide your summary as a markdown document. The filename should be `analysis_summary.md` with no directories or paths.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "analysis_summary"
    },
    {
      "type": "write_files",
      "artifact": "analysis_summary",
      "root": "{{output_root}}"
    }
  ]
}


=== File: tools/blueprint_cli/recipes/evaluate_candidate_spec.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{candidate_spec_path}}",
      "artifact": "candidate_spec"
    },
    {
      "type": "read_files",
      "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
      "artifact": "component_docs_spec_guide",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy",
      "optional": true
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer evaluating a candidate component specification to determine if it has enough context for effective implementation. You'll analyze the candidate specification and identify any areas that need clarification or additional information.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id}}\n\n{% if component_docs_spec_guide %}\nUse the following guide as your evaluation criteria:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n{% endif %}\n\n{% if implementation_philosophy %}\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n{% endif %}\n\n{% if modular_design_philosophy %}\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% endif %}\n\nPerform a systematic evaluation of the candidate specification with these steps:\n\n1. Identify the component name and type (if possible)\n2. Determine if a clear purpose statement exists\n3. Check if core requirements are well-defined and specific\n4. Assess if implementation considerations are provided\n5. Evaluate whether component dependencies are properly identified\n6. Check if error handling approaches are specified\n7. Look for any information about future considerations\n\nFor each aspect, provide:\n- A score from 1-5 (1=Missing/Insufficient, 5=Excellent)\n- Brief explanation of the score\n- Specific clarification questions if the score is 3 or lower\n\nFormat your response with these sections:\n1. Overall Assessment - Brief overview with readiness determination\n2. Scoring Summary - Table with scores for each aspect\n3. Detailed Analysis - Detailed assessment of each aspect with clarification questions\n4. Improvement Recommendations - List of questions to improve the specification\n\nBe constructive but thorough in your assessment.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "evaluation_result"
    },
    {
      "type": "generate",
      "prompt": "Format the specification evaluation as a proper markdown file with informative title and sections.\n\nEvaluation Result:\n{{evaluation_result}}\n\nComponent ID: {{component_id}}\n\nFormat your response as a structured markdown file. \n\nIf the evaluation determined that the specification needs significant clarification (average score below 4.0), name the file '{{component_id}}_needs_clarification.md'. If the specification was deemed sufficient (average score 4.0 or higher), name the file '{{component_id}}_evaluation_summary.md'.\n\nDo not include any subdirectories in the path.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "formatted_evaluation"
    },
    {
      "type": "write_files",
      "artifact": "formatted_evaluation",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: tools/blueprint_cli/recipes/generate_clarification_answers.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{candidate_spec_path}}",
      "artifact": "candidate_spec"
    },
    {
      "type": "read_files",
      "path": "{{clarification_questions_path}}",
      "artifact": "clarification_questions"
    },
    {
      "type": "read_files",
      "path": "{{context_files}}",
      "artifact": "context_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
      "artifact": "component_docs_spec_guide",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy",
      "optional": true
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer helping to improve a candidate component specification by answering clarification questions. Based on the candidate specification, the clarification questions, the provided context files, and understanding of effective component design, create an comprehensive set of answers that would help make the specification complete and implementable.\n\nCandidate Specification:\n{{candidate_spec}}\n\nClarification Questions:\n<CLARIFICATION_QUESTIONS>\n{{clarification_questions}}\n</CLARIFICATION_QUESTIONS>\n\n{% if context_content %}\nContext Files:\n<CONTEXT_FILES>\n{{context_content}}\n</CONTEXT_FILES>\n{% endif %}\n\n{% if component_docs_spec_guide %}\nUse the following guide to understand what information is needed in an effective specification:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n{% endif %}\n\n{% if implementation_philosophy %}\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n{% endif %}\n\n{% if modular_design_philosophy %}\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% endif %}\n\nEnsure your answers are clear, specific, and directly relevant to the candidate specification. For each question, provide a detailed answer that addresses the question and explains why this information is important for implementation. If a question is not applicable or cannot be answered, explain why.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "clarification_answers"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer improving a candidate component specification by incorporating answers obtained for some clarifying questions that were asked of the current candidate specification. Based on the candidate specification, the clarification questions and answers, the provided context files, and understanding of effective component design, create an updated version of the specification that is more complete and implementable.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id|default:'unknown'}}\n\nClarification Questions:\n<CLARIFICATION_QUESTIONS>\n{{clarification_questions}}\n</CLARIFICATION_QUESTIONS>\n\nClarification Answers:\n<CLARIFICATION_ANSWERS>\n{{clarification_answers}}\n</CLARIFICATION_ANSWERS>\n\n{% if context_content %}\nContext Files:\n<CONTEXT_FILES>\n{{context_content}}\n</CONTEXT_FILES>\n{% endif %}\n\n{% if component_docs_spec_guide %}\nUse the following guide to understand what information is needed in an effective specification:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n{% endif %}\n\n{% if implementation_philosophy %}\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n{% endif %}\n\n{% if modular_design_philosophy %}\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% endif %}\n\nEnsure your updates are clear, specific, and directly relevant to the candidate specification scope of work. While you are aware of the rest of the project beyond this component, this specification is meant to be built in isolation from the rest by someone who will not have context on the other components or surrounding system, so please write it up accordingly.\n\nFormat your response as a structured markdown document named exactly '{{component_id}}_candidate_spec_revised.md'. Do not include any subdirectories in the path.\n\nThe revised specification should follow this structure:\n\n# {Component Name} Component\n\n## Purpose\n[Clear, concise statement of the component's primary responsibility]\n\n## Core Requirements\n[Bulleted list of essential capabilities this component must provide]\n\n## Implementation Considerations\n[Guidance on implementation approach, constraints, challenges, etc.]\n\n## Component Dependencies\n[List of other components, external libraries, etc. this component depends on]\n\n## Error Handling\n[How this component should handle and report errors]\n\n## Output Files\n[List of files that should be generated for this component]\n\n## Future Considerations\n[Potential future enhancements or extensions]",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "revised_candidate_spec"
    },
    {
      "type": "write_files",
      "artifact": "revised_candidate_spec",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: tools/blueprint_cli/recipes/generate_clarification_questions.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{candidate_spec_path}}",
      "artifact": "candidate_spec"
    },
    {
      "type": "read_files",
      "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
      "artifact": "component_docs_spec_guide",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy",
      "optional": true
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer helping to improve a candidate component specification by generating clarification questions. Based on the candidate specification and understanding of effective component design, create a comprehensive set of questions that would help make the specification complete and implementable.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id}}\n\n{% if component_docs_spec_guide %}\nUse the following guide to understand what information is needed in an effective specification:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n{% endif %}\n\n{% if implementation_philosophy %}\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n{% endif %}\n\n{% if modular_design_philosophy %}\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% endif %}\n\nGenerate clarification questions organized into these categories:\n\n1. Purpose and Scope\n- Questions about the component's primary responsibility\n- Questions about boundaries and what's out of scope\n- Questions about the problem being solved\n\n2. Functional Requirements\n- Questions about specific capabilities needed\n- Questions about user/system interactions\n- Questions about expected inputs and outputs\n\n3. Technical Requirements\n- Questions about implementation constraints\n- Questions about performance requirements\n- Questions about security considerations\n\n4. Integration and Dependencies\n- Questions about how it interacts with other components\n- Questions about external dependencies\n- Questions about interface requirements\n\n5. Error Handling and Edge Cases\n- Questions about failure scenarios\n- Questions about edge cases\n- Questions about recovery mechanisms\n\nIn each category, provide 3-5 specific questions that would help improve the specification. Make the questions clear, specific, and directly relevant to the candidate specification. For each question, briefly explain why this information is important for implementation.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "clarification_questions"
    },
    {
      "type": "generate",
      "prompt": "Format the clarification questions as a structured markdown document that can be shared with stakeholders.\n\nClarification Questions:\n{{clarification_questions}}\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id}}\n\nCreate a document with these sections:\n1. Introduction - Brief explanation of the purpose of this document and the component being specified\n2. Current Specification - A summary of the current candidate specification\n3. Key Areas Needing Clarification - Overview of the major gaps identified\n4. Detailed Questions - The clarification questions organized by category\n5. Next Steps - Guidance on how to use these questions to improve the specification\n\nThe file should be named exactly '{{component_id}}_component_clarification_questions.md'. Do not include any subdirectories in the path.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "formatted_questions"
    },
    {
      "type": "write_files",
      "artifact": "formatted_questions",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: tools/blueprint_cli/recipes/split_project.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "project_spec",
      "optional": false
    },
    {
      "type": "read_files",
      "path": "{{component_spec}}",
      "artifact": "component_spec",
      "optional": true
    },
    {
      "type": "read_files",
      "path": "{{analysis_result}}",
      "artifact": "analysis_result",
      "optional": false
    },
    {
      "type": "read_files",
      "path": "{{guidance_files}}",
      "artifact": "guidance_files_content",
      "optional": false,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{context_files}}",
      "artifact": "context_files_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{reference_docs}}",
      "artifact": "reference_docs_content",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "# Project Splitting Task\n\nYou are an expert software architect tasked with splitting a project or component into multiple sub-components based on a previous analysis.\n\n## Project Specification (overrides context files or reference docs where discrepancies)\n\n<PROJECT_SPEC>\n{{project_spec}}\n</PROJECT_SPEC>{% if component_spec_content %}\n\n## Component Specification (focus analysis on this sub-component, knowing each other sub-component from the project spec is being analyzed separately - project spec is provided for context)\n\n<COMPONENT_SPEC>\n{{ component_spec_content }}\n</COMPONENT_SPEC>{% endif %}\n\n## Analysis Result\n\n<ANALYSIS_RESULT>\n{{analysis_result_json}}\n</ANALYSIS_RESULT>\n\n## Guidance Philosophy (how to make decisions)\n\n<GUIDANCE_FILES>\n{{guidance_files_content}}\n</GUIDANCE_FILES>{% if context_files_content %}\n\n## Context Files\n\n<CONTEXT_FILES>\n{{context_files_content}}\n</CONTEXT_FILES>{% endif %}{% if reference_docs_content %}\n\n## Reference Docs\n\n<REFERENCE_DOCS>\n{{reference_docs_content}}\n</REFERENCE_DOCS>{% endif %}\n\n## Your Task\n\nCreate detailed component specifications for each component identified in the analysis result. For each component, create a complete specification that includes:\n\n1. Component name and ID (from the analysis)\n2. Purpose and responsibility\n3. Core requirements and functionality\n4. API and interfaces\n5. Dependencies (both internal and external)\n6. Implementation considerations\n7. Error handling approach\n8. Testing strategy\n\nEach component specification should be comprehensive enough that it could be implemented independently by a developer who has only this specification and the identified dependencies.\n\n## Output Format\n\nCreate a separate markdown file for each component with the exact naming pattern `<component_id>_spec.md` (ex: 'service_spec.md').",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "component_specs"
    },
    {
      "type": "write_files",
      "artifact": "component_specs",
      "root": "{{output_root}}"
    },
    {
      "type": "generate",
      "prompt": "# Components Manifest Creation\n\nYou are an expert software architect tasked with creating a manifest file that lists all generated components from the project split. The manifest should include for each component:\n\n<COMPONENT_SPECS>\n{{ component_specs }}\n</COMPONENT_SPECS>\n\n## Output Format\n\nFormat the manifest as a JSON array of objects:\n\n```json\n[\n  {\n    \"component_id\": \"component_identifier\",\n    \"component_name\": \"Human Readable Component Name\",\n    \"spec_file\": \"component_identifier_spec.md\",\n    \"description\": \"Brief description of this component\",\n    \"dependencies\": [\"dependency_1\", \"dependency_2\"]\n  }\n]\n```\n\nThe output file must be named `components_manifest.json` (with no directories or paths).",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "components_manifest"
    },
    {
      "type": "write_files",
      "artifact": "components_manifest",
      "root": "{{output_root}}"
    }
  ]
}


=== File: tools/blueprint_cli/review_manager.py ===
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


=== File: tools/blueprint_cli/sample/docs/architecture.md ===


=== File: tools/blueprint_cli/sample/docs/external_apis/openweather_api.md ===


=== File: tools/blueprint_cli/sample/docs/external_apis/weatherstack_api.md ===


=== File: tools/blueprint_cli/sample/docs/performance_requirements.md ===


=== File: tools/blueprint_cli/sample/docs/weather_providers.md ===


=== File: tools/blueprint_cli/sample/sample_project_spec.md ===
# Weather Service API

## Overview

This project is a RESTful API service that provides weather information for specified locations. It will integrate with external weather data providers, process and cache the data, and serve it through a clean, well-documented API.

## Requirements

- Fetch current weather conditions for a specified location
- Provide 5-day weather forecasts for specified locations
- Support location specification by city name, coordinates, or zip code
- Cache weather data to reduce calls to external services
- Implement rate limiting to prevent abuse
- Provide detailed error handling and logging
- Support multiple external weather data providers for redundancy
- Include authentication for API access

## Technical Constraints

- Use FastAPI for the API framework
- PostgreSQL for persistent storage
- Redis for caching
- Docker for containerization
- Support horizontal scaling for high availability
- Implement async I/O for better performance

## Implementation Guidelines

The service should follow a clean architecture with clear separation of concerns. It should be designed to allow easy addition of new weather data providers, and easy modification of the processing pipeline. Error handling should be comprehensive, with appropriate error messages for various failure modes.

Cache invalidation should be time-based, with different TTLs for different types of data. Authentication should use JWT tokens. The API should include appropriate rate limiting to prevent abuse, while still allowing legitimate high-volume users.

## File References

### Context Files

- `docs/architecture.md`: Detailed architecture and design decisions
- `docs/weather_providers.md`: Information about weather data providers and their APIs
- `docs/performance_requirements.md`: Performance and scaling requirements

### Reference Docs

- `docs/external_apis/openweather_api.md`: OpenWeather API documentation
- `docs/external_apis/weatherstack_api.md`: WeatherStack API documentation


=== File: tools/blueprint_cli/splitter.py ===
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


=== File: tools/blueprint_cli/utils.py ===
"""
Utility functions for the Blueprint CLI tool.

This module provides common utility functions used throughout the tool.
"""

import logging
import os
import sys
import threading
from typing import Dict, List, Optional

from config import ProjectConfig

# Global print lock to prevent output interleaving
print_lock = threading.Lock()


def pause_for_user(config: ProjectConfig) -> None:
    """
    Pause for user input if auto_run is not enabled.

    Args:
        config: Project configuration
    """
    return  # disabled
    if config.auto_run:
        return

    user_input = input("Continue with the next step? (Y/n/all): ").strip().lower()
    if user_input in ["y", "yes", ""]:
        return
    elif user_input in ["n", "no"]:
        print("Exiting...")
        sys.exit(0)
    elif user_input in ["a", "all"]:
        print("Continuing with all steps...")
        config.auto_run = True
    else:
        print("Invalid input. Please enter 'Y', 'n', or 'all'.")
        pause_for_user(config)


def safe_print(*args, **kwargs):
    """
    Thread-safe print function to prevent output interleaving.

    Args:
        *args: Arguments to pass to the print function
        **kwargs: Keyword arguments to pass to the print function
    """
    with print_lock:
        print(*args, **kwargs)


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(level=level, format=log_format, handlers=[logging.StreamHandler(sys.stdout)])

    # Add file handler if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)


def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path

    Returns:
        Absolute path to the directory

    Raises:
        OSError: If directory creation fails
    """
    os.makedirs(directory, exist_ok=True)
    return os.path.abspath(directory)


def format_files_for_recipe(files: List[Dict[str, str]]) -> str:
    """
    Format a list of file dictionaries for use in a recipe.

    Args:
        files: List of {path: rationale} dictionaries

    Returns:
        Comma-separated list of file paths
    """
    return ",".join(item["path"] for item in files)


def load_file_content(file_path: str) -> str:
    """
    Load the content of a file.

    Args:
        file_path: Path to the file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file_content(file_path: str, content: str) -> None:
    """
    Write content to a file, creating directories if necessary.

    Args:
        file_path: Path to the file
        content: Content to write

    Raises:
        IOError: If file cannot be written
    """
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory(directory)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


