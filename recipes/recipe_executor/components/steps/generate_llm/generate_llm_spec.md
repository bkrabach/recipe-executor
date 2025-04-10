# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the execution context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Call LLMs to generate content
- Store generated results in the context
- Support dynamic artifact key resolution
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use template rendering for dynamic prompt generation
- Support template rendering in model selection
- Allow dynamic artifact key through template rendering
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about LLM requests

## Logging

- Debug: Log when an LLM call is being made (details of the call are handled by the LLM component)
- Info: None

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context data access and StepProtocol for the step interface (decouples from concrete Context and BaseStep classes)
- **Step Interface** – (Required) Implements the step behavior via StepProtocol
- **Context** – (Required) Uses a context implementing ContextProtocol to retrieve input values and store generation results
- **LLM** – (Required) Uses the LLM component (e.g. call_llm function) to interact with language models
- **Utils** – (Required) Uses render_template for dynamic content resolution in prompts and model identifiers

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Output Files

- `steps/generate_llm.py`

## Future Considerations

- Additional LLM parameters (e.g. temperature, max tokens, etc.)
