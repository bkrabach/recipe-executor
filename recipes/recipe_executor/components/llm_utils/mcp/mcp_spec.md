# MCP Utility Component Specification

## Purpose

The MCP utilities provide minimal, low‑level utilities for interacting with MCP servers.

## Core Requirements

- Provide a utilty method to create a PydanticAI `MCPServer` instance from a configuration object.

## Implementation Considerations

- For the `get_mcp_server` function:
  - Accept a logger and a configuration object.
  - Create an `MCPServer` instance based on the provided configuration, inferring the type of server (HTTP or stdio) from the configuration.
  - Only use the values that are necessary for the MCP server, ignore the rest.
  - Validate the configuration and raise `ValueError` if invalid.
  - Always return a PydanticAI `MCPServer` instance.

## Logging

- Debug: Log the configuration values (masking sensitive information such as keys, secrets, etc.).
- Info: For `get_mcp_server`, log the server type (HTTP or stdio) and relevant identifying information (e.g., URL, command/arg).

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic_ai.mcp**: Provides `MCPServer`, `MCPServerHTTP`, and `MCPServerStdio` classes for MCP server transports

### Configuration Dependencies

None

## Error Handling

- Wrap low‑level exceptions in `RuntimeError` or `ValueError` with descriptive messages.

## Output Files

- `recipe_executor/llm_utils/mcp.py`
