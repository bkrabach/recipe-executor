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
