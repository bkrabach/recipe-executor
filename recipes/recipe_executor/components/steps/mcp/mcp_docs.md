# McpStep Component Usage

## Importing

```python
from recipe_executor.steps.mcp import McpStep, McpConfig
```

## Configuration

The McpStep is configured with a `McpConfig`:

```python
class McpConfig(StepConfig):
    """
    Configuration for McpStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        output_key: Context key under which to store the tool output.
    """
    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    output_key: str = "tool_result"
```

## Basic Usage in Recipes

The `McpStep` is available via the `mcp` step type in recipes:

```json
{
  "steps": [
    {
      "type": "mcp",
      "config": {
        "server": {
          "url": "http://localhost:5000",
          "api_key": "your_api_key"
        },
        "tool_name": "get_stock",
        "arguments": { "item_id": "{{item_id}}" },
        "output_key": "stock_info"
      }
    }
  ]
}
```

After execution, the context contains:

```json
{
  "stock_info": {
    "item_id": 123,
    "quantity": 42
  }
}
```

## Template-Based Configuration

All string configuration fields support templating using context variables.
