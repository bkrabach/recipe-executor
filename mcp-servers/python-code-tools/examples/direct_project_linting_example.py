"""Example of using project linting with a direct MCP client."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Use the current working directory (where you run the script from)
PROJECT_PATH = os.getcwd()


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

                # Get the content text from the result with better error handling
                if result.content and len(result.content) > 0:
                    first_content = result.content[0]
                    # Check if the content is TextContent (which has a text attribute)
                    if hasattr(first_content, "type") and first_content.type == "text":
                        lint_result_text = first_content.text

                        try:
                            lint_result = json.loads(lint_result_text)

                            print(f"Project path: {lint_result.get('project_path', 'unknown')}")

                            # Display configuration information
                            config_source = lint_result.get("config_source", "unknown")
                            print(f"Configuration source: {config_source}")

                            if "config_summary" in lint_result:
                                config_summary = lint_result["config_summary"]

                                # Display each configuration source
                                for source, config in config_summary.items():
                                    if config:  # Only show non-empty configs
                                        print(f"\n{source.capitalize()} configuration:")
                                        for key, value in config.items():
                                            print(f"  {key}: {value}")

                            print(f"\nIssues found: {len(lint_result.get('issues', []))}")

                            # Group issues by file
                            issues_by_file = {}
                            for issue in lint_result.get("issues", []):
                                file_path = issue.get("file", "unknown")
                                if file_path not in issues_by_file:
                                    issues_by_file[file_path] = []
                                issues_by_file[file_path].append(issue)

                            # Print issues grouped by file
                            for file_path, issues in issues_by_file.items():
                                print(f"\nFile: {file_path}")
                                for issue in issues:
                                    print(
                                        f"  Line {issue.get('line', '?')}, Col {issue.get('column', '?')}: "
                                        f"{issue.get('code', '?')} - {issue.get('message', 'Unknown issue')}"
                                    )

                            print(f"\nFixed issues: {lint_result.get('fixed_count', 0)}")
                            print(f"Remaining issues: {lint_result.get('remaining_count', 0)}")

                            # Print summary
                            if "files_summary" in lint_result and lint_result["files_summary"]:
                                print("\nFiles Summary:")
                                for file_path, summary in lint_result["files_summary"].items():
                                    print(f"- {file_path}: {summary.get('total_issues', 0)} issues")
                                    if "issue_types" in summary:
                                        print("  Issue types:")
                                        for code, count in summary["issue_types"].items():
                                            print(f"    {code}: {count}")

                            if "modified_files" in lint_result and lint_result["modified_files"]:
                                print("\nModified files:")
                                for file in lint_result["modified_files"]:
                                    print(f"- {file}")
                            else:
                                print("\nNo files were modified.")
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON response: {e}")
                    else:
                        print(
                            "Unexpected content type: "
                            f"{first_content.type if hasattr(first_content, 'type') else 'unknown'}"
                        )
                else:
                    print("No content in the response")
            except Exception as e:
                print(f"Error during linting: {e}", file=sys.stderr)
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
