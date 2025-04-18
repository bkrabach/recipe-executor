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
        endpoint (str): The MCP server URL (templated).
        service_name (str): Name of the service on the MCP server (templated).
        tool_name (str): Name of the tool to invoke (templated).
        arguments (Dict[str, Any]): Arguments to pass to the tool (templated).
        output_key (str): Context key under which to store the tool output.
        timeout (Optional[int]): Optional timeout in seconds for the call.
    """
    endpoint: str
    service_name: str
    tool_name: str
    arguments: Dict[str, Any]
    output_key: str = "output"
    timeout: Optional[int] = None
```

## Basic Usage in Recipes

The `McpStep` is available via the `mcp` step type in recipes:

```json
{
  "steps": [
    {
      "type": "mcp",
      "endpoint": "https://mcp.example.com",
      "service_name": "inventory_service",
      "tool_name": "get_stock",
      "arguments": { "item_id": "{{item_id}}" },
      "output_key": "stock_info"
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
