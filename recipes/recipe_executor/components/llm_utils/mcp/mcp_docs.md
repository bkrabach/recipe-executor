# MCP Utility Usage

## Importing

```python
from recipe_executor.llm_utils.mcp import get_mcp_server
```

## Basic Usage

```python
def get_mcp_server(
    logger: logging.Logger,
    config: MCPServerConfig
) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.
    """
```

Use the provided `MCPServer` client to connect to an MCP server for external tool calls:

```python
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import MCPServerHttpConfig
mcp_server = get_mcp_server(
    logger=logger,
    config=MCPServerHttpConfig(
        name="weather_mcp_server",
        url="http://localhost:3001/sse",
        headers={
            "Authorization": "{{token}}",
        }
    )
)

# List available tools
tools = await mcp_server.list_tools()
print([t.name for t in tools.tools])

# Call a specific tool
result = await mcp_server.call_tool("get_stock", {"item_id": 123})
print(result)
```

## Error Handling

Tools list and calls will raise exceptions on failures:

```python
try:
    result = await client.call_tool("bad_tool", {})
except RuntimeError as e:
    print(f"Tool call failed: {e}")
```

## Important Notes

- **MCPServer** does not maintain an active connection to the server. Each tool list/call creates a new connection.
