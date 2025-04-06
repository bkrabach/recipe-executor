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
