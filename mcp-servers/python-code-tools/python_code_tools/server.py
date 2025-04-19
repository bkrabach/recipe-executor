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
    async def lint_code(code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
