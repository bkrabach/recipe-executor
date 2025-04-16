# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the execution context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Support multiple response formats (text, files, JSON)
- For JSON responses, validate against a provided schema
- Call LLMs to generate content
- Store generated results in the context with dynamic key support
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use `render_template` for templating prompts, model identifiers, and response keys
- If `response_format` is an object (JSON schema):
  - Validate via `jsonschema.validate` against the provided schema
  - Pass the JSON schema to the LLM call as the `output_type` parameter
- If `response_format` is "files":
  - Ensure the LLM response is a list of file specifications
  - Pass `List[FileSpec]` to the LLM call as the `output_type` parameter

## Logging

- Debug: Log when an LLM call is being made (details of the call are handled by the LLM component)
- Info: None

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol for context data access and StepProtocol for the step interface (decouples from concrete Context and BaseStep classes)
- **Step Interface**: Implements the step behavior via `StepProtocol`
- **Context**: Uses a context implementing `ContextProtocol` to retrieve input values and store generation responses
- **Models**: Uses the `FileSpec` model for file generation responses
- **LLM**: Uses the LLM component (e.g. `call_llm` function) to interact with language models
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

- `steps/generate_with_llm.py`
