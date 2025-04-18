# LLMGenerateStep Component Specification

## Purpose

The LLMGenerateStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, MCP server tools, structured output, and storing generation results in the execution context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Support MCP server configuration for tool access
- Support multiple output formats (text, files, JSON)
- For JSON output, validate against a provided schema
- Call LLMs to generate content
- Store generated results in the context with dynamic key support
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use `render_template` for templating prompts, model identifiers, mcp server configs, and output key
- Convert any MCP Server configurations to `MCPServerConfig` instances (`MCPServerHttpConfig` or `MCPServerStdioConfig`) to pass as `mcp_servers` to the LLM component
- If `output_format` is an object (JSON schema):
  - Validate via `jsonschema.validate` against the provided schema
  - Pass the JSON schema to the LLM call as the `output_type` parameter
- If `output_format` is "files":
  - Use `FileSpecCollection` model to pass the schema to the LLM call:
    ```python
    class FileSpecCollection(BaseModel):
        files: List[FileSpec]
    ```
  - Store the `files` value (not the entire `FileSpecCollection`) in the context
- Instantiate the `LLM` component with optional MCP servers from context config:
  ```python
  mcp_servers = context.get_config().get("mcp_servers", [])
  llm = LLM(logger, model=config.model, mcp_servers=mcp_servers)
  ```
- Use `await llm.generate(prompt, output_type=...)` to perform the generation call

## Logging

- Debug: Log when an LLM call is being made (details of the call are handled by the LLM component)
- Info: None

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol for context data access and StepProtocol for the step interface (decouples from concrete Context and BaseStep classes)
- **Step Interface**: Implements the step behavior via `StepProtocol`
- **Context**: Uses a context implementing `ContextProtocol` to retrieve input values and store generation output
- **Models**: Uses the `FileSpec` model for file generation output and `MCPServerConfig`, `MCPServerHttpConfig`, and `MCPServerStdioConfig` for MCP server configurations
- **LLM**: Uses the LLM component class `LLM` from `llm_utils.llm` to interact with language models and optional MCP servers
- **Utils**: Uses `render_template` for dynamic content resolution in prompts and model identifiers

### External Libraries

- **jsonschema** – (Installed) For JSON schema validation

### Configuration Dependencies

None

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Output Files

- `steps/llm_generate.py`
