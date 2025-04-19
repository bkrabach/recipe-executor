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
