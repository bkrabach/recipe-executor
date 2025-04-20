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
    unused_variable = 42  # unused variable
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

                    # Print the raw response for debugging
                    print(f"Response debug: {lint_result_text}")

                    lint_result = json.loads(lint_result_text)

                    # Calculate total issues
                    fixed_count = lint_result.get("fixed_count", 0)
                    remaining_count = lint_result.get("remaining_count", 0)
                    total_issues = fixed_count + remaining_count

                    print(f"Total issues found: {total_issues}")
                    print(f"Fixed issues: {fixed_count}")
                    print(f"Remaining issues: {remaining_count}")

                    print("\nFixed code:")
                    print("------------")
                    print(lint_result["fixed_code"])
                    print("------------")

                    # Show remaining issues if any
                    if remaining_count > 0:
                        print("\nRemaining issues:")
                        for issue in lint_result["issues"]:
                            print(
                                f"- Line {issue['line']}, Col {issue['column']}: {issue['code']} - {issue['message']}"
                            )
                    else:
                        print("\nAll issues were fixed!")

                    # Compare with original code
                    if fixed_count > 0:
                        print("\nChanges made:")
                        # A simple diff would be ideal here, but for simplicity we'll just highlight
                        # that changes were made
                        print(f"- Fixed {fixed_count} issues with the code")

                        if lint_result["fixed_code"] != SAMPLE_CODE:
                            print("- Code was modified during fixing")
                        else:
                            print("- NOTE: Code appears unchanged despite fixes")
                else:
                    print(
                        "Unexpected content type: "
                        f"{first_content.type if hasattr(first_content, 'type') else 'unknown'}"
                    )
            else:
                print("No content in the response")


if __name__ == "__main__":
    asyncio.run(main())
