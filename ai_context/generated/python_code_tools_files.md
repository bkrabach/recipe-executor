=== File: mcp-servers/python-code-tools/README.md ===
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


=== File: mcp-servers/python-code-tools/examples/README.md ===
# Python Code Tools Examples

This directory contains example code demonstrating how to use the Python Code Tools MCP server with different clients and tools.

## Example Files

### Code Linting Examples

- **stdio_client_example.py**: Shows how to use the `lint_code` tool with pydantic-ai's Agent class via stdio transport
- **direct_mcp_client_example.py**: Shows how to use the `lint_code` tool with a direct MCP client via stdio transport

### Project Linting Examples

- **project_linting_example.py**: Shows how to use the `lint_project` tool with pydantic-ai's Agent class
- **direct_project_linting_example.py**: Shows how to use the `lint_project` tool with a direct MCP client

## Usage Examples

### Linting a Code Snippet

Using pydantic-ai:

````python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Sample Python code with some issues
SAMPLE_CODE = """
import sys
import os
import time  # unused import

def calculate_sum(a, b):
    result = a + b
    return result

# Line too long - will be flagged by ruff
long_text = "This is a very long line of text that exceeds the default line length limit in most Python style guides"
"""

async def main():
    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-5-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"""
            Please analyze this Python code using the lint_code tool:

            ```python
            {SAMPLE_CODE}
            ```

            Explain what issues were found and what was fixed.
            """
        )

        print(result.output)

if __name__ == "__main__":
    asyncio.run(main())
````

Using a direct MCP client:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Sample code with issues
SAMPLE_CODE = """
import os
import time  # unused import

unused_var = 10
"""

async def main():
    # Create parameters for the stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "python_code_tools", "stdio"],
        env=dict(os.environ)
    )

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # Call the lint_code tool
            result = await session.call_tool(
                "lint_code",
                {
                    "code": SAMPLE_CODE,
                    "fix": True
                }
            )

            # Process the result
            if result.content and len(result.content) > 0:
                first_content = result.content[0]
                if hasattr(first_content, "type") and first_content.type == "text":
                    lint_result = json.loads(first_content.text)
                    print(f"Fixed code:\n{lint_result['fixed_code']}")
```

### Linting a Project

Using pydantic-ai:

````python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

async def main():
    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-5-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        result = await agent.run(
            """
            Please analyze the Python code in the project directory "/path/to/your/project"
            using the lint_project tool. Focus on the src directory with this command:

            ```
            lint_project(
                project_path="/path/to/your/project",
                file_patterns=["src/**/*.py"],
                fix=True
            )
            ```

            Explain what issues were found and what was fixed.
            """
        )

        print(result.output)
````

Using a direct MCP client:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Create parameters for the stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "python_code_tools", "stdio"],
        env=dict(os.environ)
    )

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # Call the lint_project tool
            result = await session.call_tool(
                "lint_project",
                {
                    "project_path": "/path/to/your/project",
                    "file_patterns": ["**/*.py"],
                    "fix": True
                }
            )

            # Process the result
            lint_result = json.loads(result.content[0].text)
            print(f"Issues found: {len(lint_result['issues'])}")
            print(f"Fixed issues: {lint_result['fixed_count']}")
```

## Additional Examples

Check the individual example files for more detailed usage patterns, including:

- Error handling
- Processing and displaying results
- Configuring tool parameters
- Working with different transport options


=== File: mcp-servers/python-code-tools/examples/direct_mcp_client_example.py ===
"""Example of using the Python Code Tools MCP server with a direct MCP client."""

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Sample Python code with some issues
SAMPLE_CODE = """
import sys
import os
import time  # unused import

def calculate_sum(a, b):
    result = a + b
    return result

# Line too long - will be flagged by ruff
long_text = "This is a very long line of text that exceeds the default line length limit in most Python style guides"
"""  # noqa: E501


async def main():
    # Create parameters for the stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "python_code_tools", "stdio"],
        env=dict(os.environ),  # Convert _Environ to regular dict
    )

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("Connected to Python Code Tools MCP server")

            # List available tools
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"Available tools: {tool_names}")

            # Call the lint_code tool
            result = await session.call_tool("lint_code", {"code": SAMPLE_CODE, "fix": True})

            # Display the results
            print("\nLint Results:")

            # Get the content text from the result
            if result.content and len(result.content) > 0:
                first_content = result.content[0]
                # Check if the content is TextContent (which has a text attribute)
                if hasattr(first_content, "type") and first_content.type == "text":
                    lint_result_text = first_content.text
                    lint_result = json.loads(lint_result_text)

                    print(f"Fixed code:\n{lint_result['fixed_code']}")
                    print(f"\nIssues found: {len(lint_result['issues'])}")

                    for issue in lint_result["issues"]:
                        print(
                            f"- Line {issue['line']}, Col {issue['column']}: "
                            f"{issue['code']} - {issue['message']}"
                        )

                    print(f"\nFixed issues: {lint_result['fixed_count']}")
                    print(f"Remaining issues: {lint_result['remaining_count']}")
                else:
                    print(
                        "Unexpected content type: "
                        f"{first_content.type if hasattr(first_content, 'type') else 'unknown'}"
                    )
            else:
                print("No content in the response")


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/examples/direct_project_linting_example.py ===
"""Example of using project linting with a direct MCP client."""

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Create parameters for the stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "python_code_tools", "stdio"],
        env=dict(os.environ),  # Convert _Environ to regular dict
    )

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("Connected to Python Code Tools MCP server")

            # List available tools
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"Available tools: {tool_names}")

            # Specify your project path
            project_path = "/path/to/your/project"

            # Call the lint_project tool
            result = await session.call_tool(
                "lint_project",
                {
                    "project_path": project_path,
                    "file_patterns": ["**/*.py"],  # All Python files in the project
                    "fix": True,
                },
            )

            # Display the results
            print("\nProject Lint Results:")

            # Get the content text from the result
            if result.content and len(result.content) > 0:
                first_content = result.content[0]
                # Check if the content is TextContent (which has a text attribute)
                if hasattr(first_content, "type") and first_content.type == "text":
                    lint_result_text = first_content.text
                    lint_result = json.loads(lint_result_text)

                    print(f"Project path: {lint_result.get('project_path', 'unknown')}")
                    print(f"Issues found: {len(lint_result['issues'])}")

                    # Print whether project has Ruff configuration
                    has_config = lint_result.get("has_ruff_config", False)
                    print(f"Project has Ruff configuration: {has_config}")

                    # Group issues by file
                    issues_by_file = {}
                    for issue in lint_result["issues"]:
                        file_path = issue.get("file", "unknown")
                        if file_path not in issues_by_file:
                            issues_by_file[file_path] = []
                        issues_by_file[file_path].append(issue)

                    # Print issues grouped by file
                    for file_path, issues in issues_by_file.items():
                        print(f"\nFile: {file_path}")
                        for issue in issues:
                            print(
                                f"  Line {issue['line']}, Col {issue['column']}: "
                                f"{issue['code']} - {issue['message']}"
                            )

                    print(f"\nFixed issues: {lint_result['fixed_count']}")
                    print(f"Remaining issues: {lint_result['remaining_count']}")

                    # Print summary
                    if "files_summary" in lint_result and lint_result["files_summary"]:
                        print("\nFiles Summary:")
                        for file_path, summary in lint_result["files_summary"].items():
                            print(f"- {file_path}: {summary['total_issues']} issues")
                            if "issue_types" in summary:
                                print("  Issue types:")
                                for code, count in summary["issue_types"].items():
                                    print(f"    {code}: {count}")

                    if "modified_files" in lint_result and lint_result["modified_files"]:
                        print("\nModified files:")
                        for file in lint_result["modified_files"]:
                            print(f"- {file}")
                else:
                    print(
                        "Unexpected content type: "
                        f"{first_content.type if hasattr(first_content, 'type') else 'unknown'}"
                    )
            else:
                print("No content in the response")


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/examples/project_linting_example.py ===
"""Example of project-based linting with Python Code Tools MCP server."""

import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


async def main():
    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-5-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        print("Connected to Python Code Tools MCP server via stdio")

        # Example conversation
        result = await agent.run(
            """
            Please analyze the Python code in the project directory "/path/to/your/project"
            using the lint_project tool. Focus on the src directory with this command:

            ```
            lint_project(
                project_path="/path/to/your/project",
                file_patterns=["src/**/*.py"],
                fix=True
            )
            ```

            Explain what issues were found and what was fixed.
            """
        )

        print("\nAgent's response:")
        print(result.output)


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/examples/stdio_client_example.py ===
"""Example client using stdio transport with the Python Code Tools MCP server."""

import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Sample Python code with some issues
SAMPLE_CODE = """
import sys
import os
import time  # unused import

def calculate_sum(a, b):
    result = a + b
    return result

# Line too long - will be flagged by ruff
long_text = "This is a very long line of text that exceeds the default line length limit in most Python style guides like PEP 8 which recommends 79 characters."
"""  # noqa: E501


async def main():
    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-5-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        print("Connected to Python Code Tools MCP server via stdio")

        # Example conversation
        result = await agent.run(
            f"""
            Please analyze this Python code using the lint_code tool:

            ```python
            {SAMPLE_CODE}
            ```

            Explain what issues were found and what was fixed.
            """
        )

        print("\nAgent's response:")
        print(result.output)


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/pyproject.toml ===
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "python-code-tools"
version = "0.1.0"
description = "MCP server providing Python code quality tools"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "your.email@example.com" }]
dependencies = ["pydantic>=2.7.2,<3.0.0", "mcp>=1.6.0", "ruff>=0.1.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "black>=23.0.0", "mypy>=1.0.0"]

[project.scripts]
# Main entry point
python-code-tools = "python_code_tools.cli:main"

# Convenience scripts for specific transports
python-code-tools-stdio = "python_code_tools.cli:stdio_main"
python-code-tools-sse = "python_code_tools.cli:sse_main"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]


=== File: mcp-servers/python-code-tools/pyrightconfig.json ===
{
  "extraPaths": ["./"],
  "typeCheckingMode": "basic"
}


=== File: mcp-servers/python-code-tools/python_code_tools/__init__.py ===
"""Python Code Tools MCP server package."""

__version__ = "0.1.0"


=== File: mcp-servers/python-code-tools/python_code_tools/__main__.py ===
"""Entry point for running the package as a module."""

from python_code_tools.cli import main

if __name__ == "__main__":
    main()


=== File: mcp-servers/python-code-tools/python_code_tools/cli.py ===
"""Command-line interface for the Python Code Tools MCP server."""

import argparse
import sys
from typing import List, Optional

from python_code_tools.server import create_mcp_server


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Python Code Tools MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Port for SSE server (default: 3001)",
    )

    args = parser.parse_args(argv)

    try:
        # Create the MCP server with the specified settings
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the server with the appropriate transport
        print(f"Starting Python Code Tools MCP server with {args.transport} transport")
        if args.transport == "sse":
            print(f"Server URL: http://{args.host}:{args.port}/sse")

        mcp.run(transport=args.transport)
        return 0
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def stdio_main() -> int:
    """Convenience entry point for stdio transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    return main(["stdio"])


def sse_main() -> int:
    """Convenience entry point for SSE transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Get any command-line arguments after the script name
    argv = sys.argv[1:]

    # Pre-populate the 'transport' argument
    all_args = ["sse"] + argv

    return main(all_args)


if __name__ == "__main__":
    sys.exit(main())


=== File: mcp-servers/python-code-tools/python_code_tools/linters/__init__.py ===
"""Project-based Ruff linter implementation."""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import ProjectLinter, ProjectLintResult


class RuffProjectLinter(ProjectLinter):
    """Project linter implementation using Ruff."""

    def __init__(self, **kwargs):
        """Initialize the project linter.

        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(name="ruff-project", **kwargs)

    async def lint_project(
        self,
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> ProjectLintResult:
        """Lint a project directory using Ruff.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include (e.g., ["*.py", "src/**/*.py"])
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for Ruff

        Returns:
            A ProjectLintResult object containing the issues found and fix counts
        """
        # Validate that the path exists and is a directory
        path = Path(project_path)
        if not path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        if not path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Check if there's a pyproject.toml or ruff.toml in the project directory
        pyproject_path = path / "pyproject.toml"
        ruff_toml_path = path / "ruff.toml"
        has_ruff_config = pyproject_path.exists() or ruff_toml_path.exists()

        # Build the ruff command
        cmd = ["ruff", "check"]

        # Add file patterns if provided
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")  # Default to checking the entire directory

        # Add fix flag if requested
        if fix:
            cmd.append("--fix")

        # Add output format for easier parsing
        cmd.extend(["--output-format", "json"])

        # Add any config options
        if config:
            for key, value in config.items():
                cmd.extend(["--config", f"{key}={value}"])

        # Print command that will be executed (for debugging)
        print(f"Executing: {' '.join(cmd)} in directory {path}")

        # Get original issue count if fixing
        original_issues_count = 0
        if fix:
            original_issues_count = await self._count_issues(path, file_patterns, config)
            print(f"Original issues count: {original_issues_count}")

        # Run ruff on the project
        issues_proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(path),  # Run from the project directory
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await issues_proc.communicate()

        # Check for errors
        if issues_proc.returncode != 0 and stderr:
            error_output = stderr.decode().strip()
            if error_output:
                print(f"Ruff error: {error_output}")

        issues_output = stdout.decode()

        # Try to parse JSON output first
        try:
            json_data = json.loads(issues_output)
            # Transform JSON output to our issue format
            issues = []
            for item in json_data:
                issues.append(
                    {
                        "file": item.get("filename", ""),
                        "line": item.get("location", {}).get("row", 0),
                        "column": item.get("location", {}).get("column", 0),
                        "code": item.get("code", ""),
                        "message": item.get("message", ""),
                        "fix_available": item.get("fix", {}).get("applicability", "")
                        == "applicable",
                    }
                )
        except Exception as e:
            # Fall back to text parsing if JSON parsing fails
            print(f"JSON parsing failed: {e}, falling back to text parsing")
            issues = self._parse_ruff_output(issues_output)

        # Count remaining issues
        remaining_count = len(issues)

        # Calculate fixed count
        fixed_count = max(0, original_issues_count - remaining_count) if fix else 0

        # Get list of modified files
        modified_files = await self._get_modified_files(path) if fix else []

        # Create a summary of findings by file
        files_summary = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in files_summary:
                files_summary[file_path] = {"total_issues": 0, "issue_types": {}}

            files_summary[file_path]["total_issues"] += 1

            code = issue.get("code", "unknown")
            if code not in files_summary[file_path]["issue_types"]:
                files_summary[file_path]["issue_types"][code] = 0
            files_summary[file_path]["issue_types"][code] += 1

        return ProjectLintResult(
            issues=issues,
            fixed_count=fixed_count,
            remaining_count=remaining_count,
            modified_files=modified_files,
            project_path=str(path),
            has_ruff_config=has_ruff_config,
            files_summary=files_summary,
        )

    def _parse_ruff_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ruff output into structured issue data.

        Args:
            output: The stdout from running ruff

        Returns:
            A list of dictionaries containing structured issue data
        """
        issues = []

        for line in output.strip().split("\n"):
            if not line:
                continue

            try:
                # Parse standard ruff output format
                # example: file.py:10:5: E501 Line too long (88 > 79 characters)
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path, line_num, col_num, message = parts

                    # Extract the error code and description
                    message_parts = message.strip().split(" ", 1)
                    if len(message_parts) == 2:
                        code, description = message_parts

                        issues.append(
                            {
                                "file": file_path,
                                "line": int(line_num),
                                "column": int(col_num),
                                "code": code,
                                "message": description,
                            }
                        )
            except Exception:
                # Skip lines that don't match the expected format
                continue

        return issues

    async def _count_issues(
        self,
        path: Path,
        file_patterns: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count the number of issues in the project.

        Args:
            path: The project directory path
            file_patterns: Optional list of file patterns to include
            config: Optional configuration settings for Ruff

        Returns:
            The number of issues found in the project
        """
        # Build the command to count issues
        cmd = ["ruff", "check"]

        # Add file patterns if provided
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")  # Default to checking the entire directory

        # Add any config options
        if config:
            for key, value in config.items():
                cmd.extend(["--config", f"{key}={value}"])

        try:
            # Run ruff without fixing to get original issue count
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(path),  # Run from the project directory
                stdout=subprocess.PIPE,
            )

            stdout, _ = await result.communicate()
            output = stdout.decode()

            # Count non-empty lines in the output
            issues = [line for line in output.strip().split("\n") if line]
            return len(issues)

        except Exception:
            return 0

    async def _get_modified_files(self, path: Path) -> List[str]:
        """Get a list of files that were modified by Ruff's auto-fix.

        Uses git status to detect modified files, or falls back to a timestamp-based
        approach if git is not available.

        Args:
            path: The project directory path

        Returns:
            A list of modified file paths (relative to the project root)
        """
        # Try using git if available (most accurate for git projects)
        try:
            # Check if this is a git repository
            is_git_repo = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "rev-parse",
                "--is-inside-work-tree",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await is_git_repo.communicate()

            if is_git_repo.returncode == 0 and stdout.decode().strip() == "true":
                # Get list of modified files
                git_status = await asyncio.create_subprocess_exec(
                    "git",
                    "-C",
                    str(path),
                    "diff",
                    "--name-only",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, _ = await git_status.communicate()

                # Filter for Python files
                modified_files = [
                    line
                    for line in stdout.decode().strip().split("\n")
                    if line.endswith(".py") and line
                ]
                return modified_files
        except Exception:
            # Git not available or error occurred, fall back to another method
            pass

        # Fallback: List Python files modified in the last minute
        # This is less accurate but works when git is not available
        modified_files = []
        current_time = datetime.now().timestamp()
        one_minute_ago = current_time - 60  # 1 minute window

        # Use os.walk to iterate through the directory tree
        for root, _, files in os.walk(str(path)):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > one_minute_ago:
                            # Convert to relative path
                            rel_path = os.path.relpath(file_path, str(path))
                            modified_files.append(rel_path)
                    except Exception:
                        continue

        return modified_files


=== File: mcp-servers/python-code-tools/python_code_tools/linters/base.py ===
"""Base interfaces for code linters."""

import abc
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LintResult(BaseModel):
    """Result model for code linting."""

    issues: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of issues found in the code"
    )
    fixed_count: int = Field(0, description="Number of issues that were automatically fixed")
    remaining_count: int = Field(0, description="Number of issues that could not be fixed")


class CodeLintResult(LintResult):
    """Result model for single code snippet linting."""

    fixed_code: str = Field(..., description="The code after linting and fixing (if enabled)")


class ProjectLintResult(LintResult):
    """Result model for project linting."""

    modified_files: List[str] = Field(
        default_factory=list, description="List of files that were modified by auto-fixes"
    )
    project_path: str = Field(..., description="Path to the project directory that was linted")
    has_ruff_config: bool = Field(
        False, description="Whether the project has a ruff configuration file"
    )
    files_summary: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Summary of issues by file"
    )


class BaseLinter(abc.ABC):
    """Abstract base class for all linters."""

    def __init__(self, name: str, **kwargs):
        """Initialize the linter.

        Args:
            name: The name of the linter
            **kwargs: Additional configuration options
        """
        self.name = name
        self.config = kwargs


class CodeLinter(BaseLinter):
    """Abstract base class for code snippet linters."""

    @abc.abstractmethod
    async def lint_code(
        self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None
    ) -> CodeLintResult:
        """Lint the provided code snippet and return the results.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A CodeLintResult object containing the fixed code and issue details
        """
        pass


class ProjectLinter(BaseLinter):
    """Abstract base class for project directory linters."""

    @abc.abstractmethod
    async def lint_project(
        self,
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> ProjectLintResult:
        """Lint a project directory and return the results.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A ProjectLintResult object containing issues found and fix details
        """
        pass


=== File: mcp-servers/python-code-tools/python_code_tools/linters/project.py ===
"""Project-based Ruff linter implementation."""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import ProjectLinter, ProjectLintResult


class RuffProjectLinter(ProjectLinter):
    """Project linter implementation using Ruff."""

    def __init__(self, **kwargs):
        """Initialize the project linter.

        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(name="ruff-project", **kwargs)

    async def lint_project(
        self,
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> ProjectLintResult:
        """Lint a project directory using Ruff.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include (e.g., ["*.py", "src/**/*.py"])
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for Ruff

        Returns:
            A ProjectLintResult object containing the issues found and fix counts
        """
        # Validate that the path exists and is a directory
        path = Path(project_path)
        if not path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        if not path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Check if there's a pyproject.toml or ruff.toml in the project directory
        pyproject_path = path / "pyproject.toml"
        ruff_toml_path = path / "ruff.toml"
        has_ruff_config = pyproject_path.exists() or ruff_toml_path.exists()

        # Build the ruff command
        cmd = ["ruff", "check"]

        # Add file patterns if provided
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")  # Default to checking the entire directory

        # Add fix flag if requested
        if fix:
            cmd.append("--fix")

        # Add output format for easier parsing
        cmd.extend(["--output-format", "json"])

        # Add any config options
        if config:
            for key, value in config.items():
                cmd.extend(["--config", f"{key}={value}"])

        # Print command that will be executed (for debugging)
        print(f"Executing: {' '.join(cmd)} in directory {path}")

        # Get original issue count if fixing
        original_issues_count = 0
        if fix:
            original_issues_count = await self._count_issues(path, file_patterns, config)
            print(f"Original issues count: {original_issues_count}")

        # Run ruff on the project
        issues_proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(path),  # Run from the project directory
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await issues_proc.communicate()

        # Check for errors
        if issues_proc.returncode != 0 and stderr:
            error_output = stderr.decode().strip()
            if error_output:
                print(f"Ruff error: {error_output}")

        issues_output = stdout.decode()

        # Try to parse JSON output first
        try:
            json_data = json.loads(issues_output)
            # Transform JSON output to our issue format
            issues = []
            for item in json_data:
                issues.append(
                    {
                        "file": item.get("filename", ""),
                        "line": item.get("location", {}).get("row", 0),
                        "column": item.get("location", {}).get("column", 0),
                        "code": item.get("code", ""),
                        "message": item.get("message", ""),
                        "fix_available": item.get("fix", {}).get("applicability", "")
                        == "applicable",
                    }
                )
        except Exception as e:
            # Fall back to text parsing if JSON parsing fails
            print(f"JSON parsing failed: {e}, falling back to text parsing")
            issues = self._parse_ruff_output(issues_output)

        # Count remaining issues
        remaining_count = len(issues)

        # Calculate fixed count
        fixed_count = max(0, original_issues_count - remaining_count) if fix else 0

        # Get list of modified files
        modified_files = await self._get_modified_files(path) if fix else []

        # Create a summary of findings by file
        files_summary = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in files_summary:
                files_summary[file_path] = {"total_issues": 0, "issue_types": {}}

            files_summary[file_path]["total_issues"] += 1

            code = issue.get("code", "unknown")
            if code not in files_summary[file_path]["issue_types"]:
                files_summary[file_path]["issue_types"][code] = 0
            files_summary[file_path]["issue_types"][code] += 1

        return ProjectLintResult(
            issues=issues,
            fixed_count=fixed_count,
            remaining_count=remaining_count,
            modified_files=modified_files,
            project_path=str(path),
            has_ruff_config=has_ruff_config,
            files_summary=files_summary,
        )

    def _parse_ruff_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ruff output into structured issue data.

        Args:
            output: The stdout from running ruff

        Returns:
            A list of dictionaries containing structured issue data
        """
        issues = []

        for line in output.strip().split("\n"):
            if not line:
                continue

            try:
                # Parse standard ruff output format
                # example: file.py:10:5: E501 Line too long (88 > 79 characters)
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path, line_num, col_num, message = parts

                    # Extract the error code and description
                    message_parts = message.strip().split(" ", 1)
                    if len(message_parts) == 2:
                        code, description = message_parts

                        issues.append(
                            {
                                "file": file_path,
                                "line": int(line_num),
                                "column": int(col_num),
                                "code": code,
                                "message": description,
                            }
                        )
            except Exception:
                # Skip lines that don't match the expected format
                continue

        return issues

    async def _count_issues(
        self,
        path: Path,
        file_patterns: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count the number of issues in the project.

        Args:
            path: The project directory path
            file_patterns: Optional list of file patterns to include
            config: Optional configuration settings for Ruff

        Returns:
            The number of issues found in the project
        """
        # Build the command to count issues
        cmd = ["ruff", "check"]

        # Add file patterns if provided
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")  # Default to checking the entire directory

        # Add any config options
        if config:
            for key, value in config.items():
                cmd.extend(["--config", f"{key}={value}"])

        try:
            # Run ruff without fixing to get original issue count
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(path),  # Run from the project directory
                stdout=subprocess.PIPE,
            )

            stdout, _ = await result.communicate()
            output = stdout.decode()

            # Count non-empty lines in the output
            issues = [line for line in output.strip().split("\n") if line]
            return len(issues)

        except Exception:
            return 0

    async def _get_modified_files(self, path: Path) -> List[str]:
        """Get a list of files that were modified by Ruff's auto-fix.

        Uses git status to detect modified files, or falls back to a timestamp-based
        approach if git is not available.

        Args:
            path: The project directory path

        Returns:
            A list of modified file paths (relative to the project root)
        """
        # Try using git if available (most accurate for git projects)
        try:
            # Check if this is a git repository
            is_git_repo = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "rev-parse",
                "--is-inside-work-tree",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await is_git_repo.communicate()

            if is_git_repo.returncode == 0 and stdout.decode().strip() == "true":
                # Get list of modified files
                git_status = await asyncio.create_subprocess_exec(
                    "git",
                    "-C",
                    str(path),
                    "diff",
                    "--name-only",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, _ = await git_status.communicate()

                # Filter for Python files
                modified_files = [
                    line
                    for line in stdout.decode().strip().split("\n")
                    if line.endswith(".py") and line
                ]
                return modified_files
        except Exception:
            # Git not available or error occurred, fall back to another method
            pass

        # Fallback: List Python files modified in the last minute
        # This is less accurate but works when git is not available
        modified_files = []
        current_time = datetime.now().timestamp()
        one_minute_ago = current_time - 60  # 1 minute window

        # Use os.walk to iterate through the directory tree
        for root, _, files in os.walk(str(path)):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > one_minute_ago:
                            # Convert to relative path
                            rel_path = os.path.relpath(file_path, str(path))
                            modified_files.append(rel_path)
                    except Exception:
                        continue

        return modified_files


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff.py ===
"""Ruff linter implementation."""

import asyncio
import subprocess
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import CodeLinter, CodeLintResult
from python_code_tools.utils.temp_file import cleanup_temp_file, create_temp_file


class RuffLinter(CodeLinter):
    """Code linter implementation using Ruff."""

    def __init__(self, **kwargs):
        """Initialize the Ruff linter.

        Args:
            **kwargs: Additional configuration options for Ruff
        """
        super().__init__(name="ruff", **kwargs)

    async def lint_code(
        self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None
    ) -> CodeLintResult:
        """Lint code using Ruff and return the results.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for Ruff

        Returns:
            A CodeLintResult object containing the fixed code and issue details
        """
        temp_file, file_path = create_temp_file(code, suffix=".py")

        try:
            # Build the ruff command
            cmd = ["ruff", "check", str(file_path)]

            # Add fix flag if requested
            if fix:
                cmd.append("--fix")

            # Add any config options
            if config:
                for key, value in config.items():
                    cmd.extend(["--config", f"{key}={value}"])

            # Run ruff to get issues
            issues_proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout, stderr = await issues_proc.communicate()
            issues_output = stdout.decode()

            # Parse issues
            issues = self._parse_ruff_output(issues_output)

            # Read the fixed code
            with open(file_path, "r") as f:
                fixed_code = f.read()

            # Determine fixed and remaining counts
            fixed_count = 0
            remaining_count = len(issues)

            if fix and code != fixed_code:
                # If code was modified, count the difference as fixes
                original_issues_count = await self._count_issues(code)
                fixed_count = max(0, original_issues_count - remaining_count)

            return CodeLintResult(
                fixed_code=fixed_code,
                issues=issues,
                fixed_count=fixed_count,
                remaining_count=remaining_count,
            )

        finally:
            # Clean up temporary file
            cleanup_temp_file(temp_file, file_path)

    def _parse_ruff_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ruff output into structured issue data.

        Args:
            output: The stdout from running ruff

        Returns:
            A list of dictionaries containing structured issue data
        """
        issues = []

        for line in output.strip().split("\n"):
            if not line:
                continue

            try:
                # Parse standard ruff output format
                # example: file.py:10:5: E501 Line too long (88 > 79 characters)
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path, line_num, col_num, message = parts

                    # Extract the error code and description
                    message_parts = message.strip().split(" ", 1)
                    if len(message_parts) == 2:
                        code, description = message_parts

                        issues.append(
                            {
                                "line": int(line_num),
                                "column": int(col_num),
                                "code": code,
                                "message": description,
                            }
                        )
            except Exception:
                # Skip lines that don't match the expected format
                continue

        return issues

    async def _count_issues(self, code: str) -> int:
        """Count the number of issues in the original code.

        Args:
            code: The Python code to analyze

        Returns:
            The number of issues found in the code
        """
        temp_file, file_path = create_temp_file(code, suffix=".py")

        try:
            # Run ruff without fixing to get original issue count
            result = await asyncio.create_subprocess_exec(
                "ruff", "check", str(file_path), stdout=subprocess.PIPE
            )

            stdout, _ = await result.communicate()
            output = stdout.decode()

            # Count non-empty lines in the output
            issues = [line for line in output.strip().split("\n") if line]
            return len(issues)

        except Exception:
            return 0
        finally:
            # Clean up
            cleanup_temp_file(temp_file, file_path)


=== File: mcp-servers/python-code-tools/python_code_tools/server.py ===
"""MCP server implementation for Python code tools."""

import argparse
import sys
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from python_code_tools.linters.project import RuffProjectLinter
from python_code_tools.linters.ruff import RuffLinter


def create_mcp_server(host: str = "localhost", port: int = 3001) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        host: The hostname for the SSE server
        port: The port for the SSE server

    Returns:
        A configured FastMCP server instance
    """
    # Initialize FastMCP server with settings for SSE transport
    mcp = FastMCP("Python Code Tools", host=host, port=port, debug=False, log_level="INFO")

    # Initialize the linters
    ruff_linter = RuffLinter()
    project_linter = RuffProjectLinter()

    @mcp.tool()
    async def lint_code(
        code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Lint Python code and optionally fix issues.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A dictionary containing the fixed code, issues found, and fix counts
        """
        result = await ruff_linter.lint_code(code, fix, config)
        return result.model_dump()

    @mcp.tool()
    async def lint_project(
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Lint a Python project directory and optionally fix issues.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include (e.g., ["*.py", "src/**/*.py"])
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A dictionary containing issues found, fix counts, and modified files
        """
        result = await project_linter.lint_project(project_path, file_patterns, fix, config)
        return result.model_dump()

    return mcp


def main() -> int:
    """Main entry point for the server CLI.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Python Code Tools MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Port for SSE server (default: 3001)",
    )

    args = parser.parse_args()

    try:
        # Create the MCP server with the specified settings
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the server with the appropriate transport
        print(f"Starting Python Code Tools MCP server with {args.transport} transport")
        if args.transport == "sse":
            print(f"Server URL: http://{args.host}:{args.port}/sse")

        mcp.run(transport=args.transport)
        return 0
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# For importing in other modules
mcp = create_mcp_server()

if __name__ == "__main__":
    sys.exit(main())


=== File: mcp-servers/python-code-tools/python_code_tools/utils/__init__.py ===
"""Utility functions for Python Code Tools."""

from python_code_tools.utils.temp_file import (
    cleanup_temp_file,
    create_temp_file,
)

__all__ = ["create_temp_file", "cleanup_temp_file"]


=== File: mcp-servers/python-code-tools/python_code_tools/utils/temp_file.py ===
"""Temporary file handling utilities."""

import os
import tempfile
from pathlib import Path
from typing import IO, Any, Tuple


def create_temp_file(content: str, suffix: str = ".txt") -> Tuple[IO[Any], Path]:
    """Create a temporary file with the given content.

    Args:
        content: The content to write to the file
        suffix: The file suffix/extension

    Returns:
        A tuple containing the temporary file object and the path to the file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file_path = Path(temp_file.name)

    with open(file_path, "w") as f:
        f.write(content)

    return temp_file, file_path


def cleanup_temp_file(temp_file: IO[Any], file_path: Path) -> None:
    """Clean up a temporary file.

    Args:
        temp_file: The temporary file object
        file_path: The path to the file
    """
    temp_file.close()
    if os.path.exists(file_path):
        os.unlink(file_path)


