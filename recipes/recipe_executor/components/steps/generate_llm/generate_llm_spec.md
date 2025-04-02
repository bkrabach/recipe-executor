# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the context.

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

- Debug: Log that the LLM call is being made (leave the details to the LLM component to log)
- Info: None

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Extends BaseStep to implement the step interface
- **Context** - (Required) Retrieves input values and stores generation results
- **LLM** - (Required) Uses call_llm function to interact with language models
- **Utils** - (Required) Uses render_template for dynamic content resolution in prompts and model identifiers

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

- Additional LLM parameters (temperature, max tokens, etc.)
