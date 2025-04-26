# MCPStep Component Specification

## Purpose

The MCPStep component allows recipes to invoke tools on remote MCP servers and store the result in the execution context.

## Core Requirements

- Accept configuration for the MCP server, tool name, arguments, and result key.
- Use a minimal MCP client implementation:
  - Connect to the MCP server using the provided configuration.
  - Call the specified tool with the provided arguments.
- Handle errors:
  - Raise a `ValueError` with a clear message if the call fails.
- Remain stateless across invocations.

## Implementation Considerations

- Retrieve configuration values via the step config object.
- Use `render_template` to resolve templated configuration values before use.
- Use `sse_client` or `stdio_client` to create `ClientSession` instance.
  - For `stdio_client`:
    - Use `StdioServerParameters` for `server` config parameter.
    - Use `cwd` as the working directory for the command.
- Intialize session and execute session.call_tool with the tool name and arguments.
- Wrap exceptions from the client in `ValueError` including the tool name and service.
- Convert the `mcp.types.CallToolResult` to `Dict[str, Any]`.
- Store converted tool result dictionary in context under `result_key`.
- Overwrite existing context values if `result_key` already exists.

## Logging

- Debug: Log connection attempts and tool invocation details (tool name, arguments).
- Info: None by default.

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for context interactions and `StepProtocol` for the step interface.
- **Utils/Templates**: Uses `render_template` for resolving templated parameters.

### External Libraries

- **mcp**: Provides `sse_client`, `stdio_client`, `CallToolResult` `StdioServerParameters` and `ClientSession` for MCP server interactions.

### Configuration Dependencies

None

## Error Handling

- Raise `ValueError` on connection failures or tool invocation errors with descriptive messages.
- Allow exceptions from the client to propagate if not caught.

## Output Files

- `recipe_executor/steps/mcp.py`
