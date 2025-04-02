# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini (not Vertex))
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI for consistent handling and validation of LLM responses
- Implement basic error handling
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Do not need to pass api keys directly to model classes (do need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing only the model name
  - pydantic_ai.models.openai.OpenAIModel (used for Azure OpenAI)
  - pydantic_ai.models.anthropic.AnthropicModel
  - pydantic_ai.models.gemini.GeminiModel
- Create a PydanticAI Agent with the model and a structured output type
- Use the `run_sync` method of the Agent to make requests
- CRITICAL: make sure to return the result.data in the call_llm method

## Logging

- Debug: Log full request payload before making call and then full response payload after receiving it
- Info: Log model name and provider before making call (do not include the request payload details) and response times upon completion (do not include the response payload details)

## Component Dependencies

### Internal Components

- **Models** - (Required) Uses FileGenerationResult and FileSpec for structured output validation
- **Azure OpenAI** - (Required for Azure provider) Uses get_azure_openai_model for Azure OpenAI model initialization

### External Libraries

- **pydantic-ai** - (Required) Relies on PydanticAI for model initialization, Agent-based request handling, and structured-output response processing

### Configuration Dependencies

- **DEFAULT_MODEL** - (Optional) Environment variable specifying the default LLM model in format "provider:model_name"
- **OPENAI_API_KEY** - (Required for OpenAI) API key for OpenAI access
- **ANTHROPIC_API_KEY** - (Required for Anthropic) API key for Anthropic access
- **GEMINI_API_KEY** - (Required for Gemini) API key for Google Gemini AI access

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `llm.py`

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning

## Dependency Integration Considerstions

### PydanticAI

Create a PydanticAI model for the LLM provider and model name. This will be used to initialize the model and make requests.

```python
def get_model(model_id: str) -> OpenAIModel | AnthropicModel | GeminiModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name' or 'provider:model_name:deployment_name'.

    Supported providers:
    - openai
    - anthropic
    - gemini
    - azure (for Azure OpenAI, use 'azure:model_name:deployment_name' or 'azure:model_name')

    Args:
        model_id (str): Model identifier in format 'provider:model_name'
            or 'provider:model_name:deployment_name'.
            If None, defaults to 'openai:gpt-4o'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai:o3-mini")
# Uses OpenAIModel('o3-mini')

# Get an Anthropic model
anthropic_model = get_model("anthropic:claude-3.7-sonnet-latest")
# Uses AnthropicModel('claude-3.7-sonnet-latest')

# Get a Gemini model
gemini_model = get_model("gemini:gemini-pro")
# Uses GeminiModel('gemini-pro')
```
