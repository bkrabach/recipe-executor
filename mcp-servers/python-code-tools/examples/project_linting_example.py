"""Example of project-based linting with Python Code Tools MCP server."""

import asyncio
import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


async def main():
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Using project path: {current_dir}")

    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-5-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        print("Connected to Python Code Tools MCP server via stdio")

        # Example conversation with actual project path
        result = await agent.run(
            f"""
            Please analyze the Python code in this project directory using the lint_project tool.

            Run this command:
            ```
            lint_project(
                project_path="{current_dir}",
                file_patterns=["**/*.py"],
                fix=True
            )
            ```

            After running the lint_project tool, provide a detailed analysis that includes:
            1. How many total issues were found (fixed + remaining)
            2. What types of issues were fixed automatically
            3. What issues remain and need manual attention
            4. Which files were modified

            Please be specific about the exact issues found and fixed.
            """
        )

        print("\nAgent's response:")
        print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
