# MCP Utility Component Specification

## Purpose

The MCP utility provides a minimal, low‑level interface for creating PydanticAI `MCPServer` instances.

## Core Requirements

- Provide a utilty method to create a PydanticAI `MCPServer` instance from a provided `MCPServerConfig`.

## Implementation Considerations

- Use `MCPServerHTTP` and `MCPServerStdio` for HTTP and stdio transports, respectively
- Validate the configuration and raise `ValueError` if invalid
- Always return a PydanticAI `MCPServer` instance

## Logging

- Debug: Log the configuration values (masking sensitive information).
- Info: Log the transport type and server URL.

## Component Dependencies

### Internal Components

- **Models**: Uses `MCPServerHttpConfig` and `MCPServerStdioConfig` for configuration, which both satisfy the `MCPServerConfig` union type
- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic_ai.mcp**: Provides `MCPServer`, `MCPServerHTTP`, and `MCPServerStdio` classes for MCP server transports

### Configuration Dependencies

None

## Error Handling

- Wrap low‑level exceptions in `RuntimeError` or `ValueError` with descriptive messages.

## Output Files

- `llm_utils/mcp.py`
