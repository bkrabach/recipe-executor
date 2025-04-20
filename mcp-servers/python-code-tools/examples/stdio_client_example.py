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
    unused_variable = 42  # unused variable
    return result

# Line too long - will be flagged by ruff
long_text = "This is a very long line of text that exceeds the default line length limit in most Python style guides like PEP 8 which recommends 79 characters, but if the configuration is set to 120, it will be ignored unless the line continues for more than 120 characters like this one now does at over 300 characters."
"""


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

            After running the lint_code tool, provide a detailed analysis that includes:
            1. How many total issues were found (fixed + remaining)
            2. What types of issues were fixed automatically
            3. What issues remain and need manual attention
            4. Show the fixed code and explain what was changed

            Please be specific about the exact issues found and fixed.

            Show the updated code with comments explaining the changes made.
            """
        )

        print("\nAgent's response:")
        print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
