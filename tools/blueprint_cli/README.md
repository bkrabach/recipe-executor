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
