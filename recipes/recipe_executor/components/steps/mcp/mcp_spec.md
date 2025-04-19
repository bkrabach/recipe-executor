# McpStep Component Specification

## Purpose

The McpStep component allows recipes to invoke tools on remote MCP servers. It creates a simple MCP client, connects to the given server endpoint, calls the specified tool with provided arguments, and stores the result in the execution context.

## Core Requirements

- Accept configuration for:
  - `endpoint`: MCP server URL (templated).
  - `service_name`: Name of the service on the MCP server.
  - `tool_name`: Name of the tool to invoke.
  - `arguments`: Dictionary of arguments to pass to the tool.
  - `result_key`: Context key under which to store the result.
- Use a minimal MCP client implementation:
  - Connect to the server if not already connected.
  - Call the specified tool with the provided arguments.
- Store the tool call result in the context under `result_key`.
- Handle errors:
  - Raise a `ValueError` with a clear message if the call fails.
- Remain stateless across invocations.

## Implementation Considerations

- Use `render_template` to resolve templated configuration values before use.
- Retrieve configuration values via the step config object.
- Instantiate or reuse an `McpClient` using `endpoint` and `service_name`.
- Call `client.call_tool(tool_name, arguments)` to invoke the tool.
- Wrap exceptions from the client in `ValueError` including the tool name and service.
- Overwrite existing context values if `result_key` already exists.

## Logging

- Debug: Log connection attempts and tool invocation details (tool name, arguments).
- Info: None by default.

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for context interactions and `StepProtocol` for the step interface.
- **Context**: Reads from and writes to the execution context.
- **MCP**: Uses `McpClient` and `create_mcp_agent` for server communication.
- **Utils**: Uses `render_template` for resolving templated parameters.

### External Libraries

- **copy**, **typing** (Python stdlib)

### Configuration Dependencies

None

## Error Handling

- Raise `ValueError` on connection failures or tool invocation errors with descriptive messages.
- Allow exceptions from the client to propagate if not caught.

## Output Files

- `steps/mcp.py`
