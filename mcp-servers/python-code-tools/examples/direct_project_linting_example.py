"""Example of using project linting with a direct MCP client."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Use the current working directory (where you run the script from)
PROJECT_PATH = os.getcwd()


def normalize_path(file_path, project_path):
    """Convert absolute paths to project-relative paths for better display.

    Args:
        file_path: Absolute or relative file path
        project_path: Base project path

    Returns:
        Simplified path for display
    """
    try:
        # If it's already a relative path, return it
        if not os.path.isabs(file_path):
            return file_path

        # Convert absolute path to relative path
        rel_path = os.path.relpath(file_path, project_path)

        # Remove leading ./ if present
        if rel_path.startswith("./"):
            rel_path = rel_path[2:]

        return rel_path
    except Exception:
        # If any error occurs, return the original path
        return file_path


async def main():
    print(f"Using project path: {PROJECT_PATH}")

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

            try:
                # Call the lint_project tool with improved error handling
                print(f"Calling lint_project tool for path: {PROJECT_PATH}")
                result = await session.call_tool(
                    "lint_project",
                    {
                        "project_path": PROJECT_PATH,
                        "file_patterns": ["**/*.py", "*.py"],  # Both top-level and nested Python files
                        "fix": True,
                    },
                )

                # Display the results
                print("\nProject Lint Results:")

                # First, check if we got any response at all
                if not result or not result.content:
                    print("Error: No response content received from the MCP server")
                    sys.exit(1)

                # Get the content text from the result with better error handling
                first_content = result.content[0] if result.content else None
                if not first_content:
                    print("Error: Empty response content")
                    sys.exit(1)

                # Check if the content is TextContent (which has a text attribute)
                if not hasattr(first_content, "type") or first_content.type != "text":
                    print(f"Error: Unexpected content type: {getattr(first_content, 'type', 'unknown')}")
                    sys.exit(1)

                lint_result_text = first_content.text
                if not lint_result_text:
                    print("Error: Empty text content in response")
                    sys.exit(1)

                # Print the raw response for debugging
                print(f"Response debug: {lint_result_text}")

                try:
                    lint_result = json.loads(lint_result_text)

                    # Check if we got an error from the server
                    if "error" in lint_result:
                        print(f"Server reported an error: {lint_result['error']}")
                        sys.exit(1)

                    project_path = lint_result.get("project_path", PROJECT_PATH)
                    print(f"Project path: {project_path}")

                    # Display configuration information
                    config_source = lint_result.get("config_source", "unknown")
                    print(f"Configuration source: {config_source}")

                    if "config_summary" in lint_result and "ruff" in lint_result["config_summary"]:
                        ruff_config = lint_result["config_summary"]["ruff"]
                        print("Ruff configuration:")
                        for key, value in ruff_config.items():
                            print(f"  {key}: {value}")

                    # Calculate total issues (sum of fixed and remaining)
                    fixed_count = lint_result.get("fixed_count", 0)
                    remaining_count = lint_result.get("remaining_count", 0)
                    total_issues_count = fixed_count + remaining_count

                    # Print issue counts
                    print(f"\nTotal issues found: {total_issues_count}")
                    print(f"Fixed issues: {fixed_count}")
                    print(f"Remaining issues: {remaining_count}")

                    # Display fixed issues
                    if lint_result.get("fixed_issues") and fixed_count > 0:
                        print("\nIssues that were fixed:")
                        fixed_issues_by_file = {}
                        for issue in lint_result.get("fixed_issues", []):
                            file_path = issue.get("file", "unknown")
                            normalized_path = normalize_path(file_path, project_path)
                            if normalized_path not in fixed_issues_by_file:
                                fixed_issues_by_file[normalized_path] = []
                            fixed_issues_by_file[normalized_path].append(issue)

                        # Print fixed issues grouped by file
                        for file_path, issues in fixed_issues_by_file.items():
                            print(f"\nFile: {file_path}")
                            for issue in issues:
                                print(
                                    f"  Line {issue.get('line', '?')}, Col {issue.get('column', '?')}: "
                                    f"{issue.get('code', '?')} - {issue.get('message', 'Unknown issue')}"
                                )

                    # Display remaining issues
                    if remaining_count > 0:
                        print("\nRemaining issues:")
                        issues_by_file = {}
                        for issue in lint_result.get("issues", []):
                            file_path = issue.get("file", "unknown")
                            normalized_path = normalize_path(file_path, project_path)
                            if normalized_path not in issues_by_file:
                                issues_by_file[normalized_path] = []
                            issues_by_file[normalized_path].append(issue)

                        # Print issues grouped by file
                        for file_path, issues in issues_by_file.items():
                            print(f"\nFile: {file_path}")
                            for issue in issues:
                                print(
                                    f"  Line {issue.get('line', '?')}, Col {issue.get('column', '?')}: "
                                    f"{issue.get('code', '?')} - {issue.get('message', 'Unknown issue')}"
                                )

                    # Print file summary
                    if "files_summary" in lint_result and lint_result["files_summary"]:
                        print("\nFiles Summary:")
                        for file_path, summary in lint_result["files_summary"].items():
                            normalized_path = normalize_path(file_path, project_path)
                            print(f"- {normalized_path}: {summary.get('total_issues', 0)} remaining issues")
                            if "issue_types" in summary:
                                print("  Issue types:")
                                for code, count in summary["issue_types"].items():
                                    print(f"    {code}: {count}")

                    # Print modified files
                    if "modified_files" in lint_result and lint_result["modified_files"]:
                        print("\nModified files:")
                        for file in lint_result["modified_files"]:
                            print(f"- {file}")
                    else:
                        print("\nNo files were modified.")

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw response text: {lint_result_text}")
            except Exception as e:
                print(f"Error during linting: {e}", file=sys.stderr)
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
