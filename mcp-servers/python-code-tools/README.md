# Python Code Tools MCP Server

This project implements a Model Context Protocol (MCP) server that provides code quality and maintenance tools for Python projects. It allows AI assistants and other MCP clients to perform code linting and fixing operations on both individual Python code snippets and entire project directories.

## Features

- **Code Linting with Auto-fix**: Uses Ruff, a fast Python linter written in Rust, to identify issues and automatically fix them where possible
- **Project-level Linting**: Analyze and fix code issues across entire Python projects or specific directories
- **Generic architecture** allows for easily swapping underlying tools in the future
- **Support for multiple transports**:
  - **stdio**: For direct subprocess communication
  - **SSE**: For HTTP-based communication
- **Convenient command-line interface** with dedicated scripts for each transport
- **Integration with AI assistants** like Claude and other MCP clients

## Requirements

- Python 3.10+
- MCP Python SDK (`pip install mcp>=1.6.0`)
- Ruff (`pip install ruff>=0.1.0`)

## Installation

### Using UV (Recommended)

1. Clone this repository
2. Create and activate a virtual environment:

```bash
# Create the virtual environment
uv venv

# Activate it (Unix/macOS)
source .venv/bin/activate
# Or on Windows
.venv\Scripts\activate
```

3. Install the package in development mode:

```bash
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

## Usage

### Command Line

The server provides several convenient entry points:

#### General Command

```bash
# Start with stdio transport
python-code-tools stdio

# Start with SSE transport
python-code-tools sse --host localhost --port 3001
```

#### Transport-Specific Commands

```bash
# Start with stdio transport
python-code-tools-stdio

# Start with SSE transport (with optional host/port args)
python-code-tools-sse
# or with custom host and port
python-code-tools-sse --host 0.0.0.0 --port 5000
```

### As a Python Module

```bash
# Using stdio transport
python -m python_code_tools stdio

# Using SSE transport
python -m python_code_tools sse --host localhost --port 3001
```

## Using with MCP Clients

See the [examples directory](./examples/README.md) for detailed examples of using the Python Code Tools MCP server with different clients and tools.

## Available Tools

### `lint_code`

Lints a Python code snippet and automatically fixes issues when possible.

**Parameters**:

- `code` (string, required): The Python code to lint
- `fix` (boolean, optional): Whether to automatically fix issues when possible (default: true)
- `config` (object, optional): Optional configuration settings for the linter

**Returns**:

- `fixed_code` (string): The code after linting and fixing
- `issues` (list): List of issues found in the code
- `fixed_count` (integer): Number of issues that were automatically fixed
- `remaining_count` (integer): Number of issues that could not be fixed

### `lint_project`

Lints a Python project directory and automatically fixes issues when possible.

**Parameters**:

- `project_path` (string, required): Path to the project directory to lint
- `file_patterns` (array of strings, optional): List of file patterns to include (e.g., `["*.py", "src/**/*.py"]`)
- `fix` (boolean, optional): Whether to automatically fix issues when possible (default: true)
- `config` (object, optional): Optional configuration settings for the linter

**Returns**:

- `issues` (array): List of issues found in the code
- `fixed_count` (integer): Number of issues that were automatically fixed
- `remaining_count` (integer): Number of issues that could not be fixed
- `modified_files` (array): List of files that were modified by the auto-fix
- `project_path` (string): The path to the project that was linted
- `has_ruff_config` (boolean): Whether the project has a ruff configuration file
- `files_summary` (object): Summary of issues grouped by file

## Extending the Server

### Adding New Linters

The server is designed to be extended with additional linters. To add a new linter:

1. Create a new class that extends the appropriate base class (`CodeLinter` or `ProjectLinter`) in a new file under `python_code_tools/linters/`
2. Implement the required methods (`lint_code()` or `lint_project()`)
3. Update the `create_mcp_server()` function in `server.py` to use your new linter

Example for a hypothetical alternative code linter:

```python
# python_code_tools/linters/alt_linter.py
from python_code_tools.linters.base import CodeLinter, CodeLintResult

class AltLinter(CodeLinter):
    """An alternative linter implementation."""

    def __init__(self, **kwargs):
        super().__init__(name="alt-linter", **kwargs)

    async def lint_code(self, code, fix=True, config=None):
        # Implement the linting logic using your tool of choice
        # ...
        return CodeLintResult(
            fixed_code=fixed_code,
            issues=issues,
            fixed_count=fixed_count,
            remaining_count=remaining_count
        )
```

Example for a hypothetical alternative project linter:

```python
# python_code_tools/linters/alt_project_linter.py
from python_code_tools.linters.base import ProjectLinter, ProjectLintResult

class AltProjectLinter(ProjectLinter):
    """An alternative project linter implementation."""

    def __init__(self, **kwargs):
        super().__init__(name="alt-project-linter", **kwargs)

    async def lint_project(self, project_path, file_patterns=None, fix=True, config=None):
        # Implement the project linting logic using your tool of choice
        # ...
        return ProjectLintResult(
            issues=issues,
            fixed_count=fixed_count,
            remaining_count=remaining_count,
            modified_files=modified_files,
            project_path=project_path,
            has_ruff_config=has_config,
            files_summary=files_summary
        )
```

### Adding New Tool Types

To add entirely new tool types beyond linting:

1. Implement the tool logic in an appropriate module
2. Add a new function to the `create_mcp_server()` function in `server.py`
3. Register it with the `@mcp.tool()` decorator
